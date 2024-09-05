from collections import defaultdict

from digital_twin_migration.database import Propagation, Transactional, db
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.resources.data.data_details import data_detail_repository
from app.schemas import EfficiencyDataDetailSchema, VariableSchema
from core.security import token_required
from core.utils import (calculate_gap, calculate_persen_losses, parse_params,
                        response)

variable_schema = VariableSchema()
data_details_schema = EfficiencyDataDetailSchema()


class DataListParetoResource(Resource):

    @token_required
    @parse_params(
        Argument("persen_threshold", location="args", type=int, required=False),
    )
    def get(self, user_id, transaction_id, persen_threshold):
        current_data = data_detail_repository.get_data_pareto(transaction_id, True)
        target_data = data_detail_repository.get_data_pareto(transaction_id, False)

        current_dict = {
            item.variable_id: (item, total_cost) for item, total_cost in current_data
        }
        target_dict = {item.variable_id: item for item in target_data}

        calculated_data = []
        aggregated_persen_losses = defaultdict(float)

        for variable_id, (current_item, total_cost) in current_dict.items():
            target_item = target_dict.get(variable_id)

            if target_item:
                gap = calculate_gap(target_item.nilai, current_item.nilai)

                if gap is None:
                    raise Exception(gap, target_item.nilai_string, current_item.nilai)

                persen_losses = calculate_persen_losses(
                    gap, current_item.deviasi, current_item.persen_hr
                )

                nilai_losses = (persen_losses / 100) * 1000

                aggregated_persen_losses[current_item.variable.category] += (
                    nilai_losses if nilai_losses is not None else 0
                )

                calculated_data.append(
                    {
                        "id": current_item.id,
                        "variable": variable_schema.dump(current_item.variable),
                        "existing_data": current_item.nilai,
                        "reference_data": target_item.nilai,
                        "deviasi": current_item.deviasi,
                        "persen_hr": current_item.persen_hr,
                        "persen_losses": persen_losses,
                        "nilai_losses": nilai_losses,
                        "gap": gap,
                        "total_biaya": total_cost,
                    }
                )

        result = []
        total_persen = 0
        # sorted aggregated_nilai_losses
        aggregated_persen_losses = dict(
            sorted(aggregated_persen_losses.items(), key=lambda x: x[1], reverse=True)
        )

        for category, losses in aggregated_persen_losses.items():
            total_persen += losses
            category_data = {
                "category": category,
                "total_persen_losses": losses,
                "total_nilai_losses": (losses / 100) * 1000,
                "data": [
                    item
                    for item in calculated_data
                    if item["variable"]["category"] == category
                ],
            }

            if persen_threshold and total_persen >= persen_threshold:
                break

            result.append(category_data)

        return response(200, True, "Data retrieved successfully", result)

    @token_required
    @parse_params(
        Argument("is_bulk", location="args", type=int, required=False, default=0),
        Argument(
            "pareto_data", location="json", type=list, required=False, default=None
        ),
        Argument("detail_id", location="json", type=str, required=False),
        Argument("deviasi", location="json", required=False, type=float),
        Argument("persen_hr", location="json", required=False, type=float),
    )
    @Transactional(propagation=Propagation.REQUIRED)
    def put(self, user_id, transaction_id, is_bulk, pareto_data, **inputs):
        if is_bulk:
            if not pareto_data:
                return response(
                    400, False, "pareto_data is required when 'is_bulk' is set"
                )

            for pareto in pareto_data:
                data_detail = data_detail_repository.get_by_uuid(pareto["detail_id"])
                if not data_detail:
                    return response(404, False, "Data Detail not found")
                data_detail_repository.update(
                    data_detail,
                    {
                        "deviasi": pareto["deviasi"],
                        "persen_hr": pareto["persen_hr"],
                        "updated_by": user_id,
                    },
                )

        else:
            missing_input = next(
                (name for name, input in inputs.items() if not input), None
            )
            if missing_input:
                return response(
                    400,
                    False,
                    f"'{missing_input}' is required when 'is_bulk' is not set",
                )

            data_detail = data_detail_repository.get_by_uuid(inputs["detail_id"])
            if not data_detail:
                return response(404, False, "Data Detail not found")

            data_detail_repository.update(
                data_detail,
                {
                    "deviasi": inputs["deviasi"],
                    "persen_hr": inputs["persen_hr"],
                    "updated_by": user_id,
                },
            )

        return response(200, True, "Data Detail updated successfully")
