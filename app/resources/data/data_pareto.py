import math
from collections import defaultdict

from digital_twin_migration.database import Propagation, Transactional, db
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.controllers.data.data_detail import data_detail_repository, data_detail_controller
from app.schemas import EfficiencyDataDetailSchema, VariableSchema
from core.cache.cache_manager import Cache
from core.security import token_required
from core.utils import (calculate_gap, calculate_persen_losses, parse_params,
                        response)

variable_schema = VariableSchema()
data_details_schema = EfficiencyDataDetailSchema()


class DataListParetoResource(Resource):

    @token_required
    @parse_params(
        Argument(
            "percent_threshold", location="args", type=int, required=False, default=None
        ),
    )
    def get(self, user_id, transaction_id, percent_threshold):

        result = data_detail_controller.get_data_pareto(transaction_id, percent_threshold)

        # data = data_detail_repository.get_data_pareto(transaction_id)
        # # target_data = data_detail_repository.get_data_pareto(transaction_id, False)

        # if data is None:
        #     return response(404, False, "Data is not available")

        # calculated_data_by_category = defaultdict(list)
        # aggregated_persen_losses = defaultdict(float)

        # total_persen = 0
        # result = []

        # for current_data, target_data, total_cost in data:
        #     gap = calculate_gap(target_data.nilai, current_data.nilai)
        #     persen_losses = calculate_persen_losses(
        #         gap, target_data.deviasi, current_data.persen_hr
        #     )
        #     nilai_losses = (persen_losses / 100) * 1000

        #     category = current_data.variable.category
        #     aggregated_persen_losses[category] += persen_losses or 0

        #     calculated_data_by_category[category].append(
        #         {
        #             "id": current_data.id,
        #             "variable": variable_schema.dump(current_data.variable),
        #             "existing_data": current_data.nilai,
        #             "reference_data": target_data.nilai,
        #             "deviasi": current_data.deviasi,
        #             "persen_hr": current_data.persen_hr,
        #             "persen_losses": persen_losses,
        #             "nilai_losses": nilai_losses,
        #             "gap": gap,
        #             "total_biaya": total_cost,
        #             "symptoms": "Higher" if gap > 0 else "Lower",
        #         }
        #     )

        # # Sort aggregated losses only once, limit looping
        # aggregated_persen_losses = dict(
        #     sorted(aggregated_persen_losses.items(), key=lambda x: x[1], reverse=True)
        # )

        # for category, losses in aggregated_persen_losses.items():
        #     total_persen += losses
        #     if percent_threshold and total_persen >= percent_threshold:
        #         break

        #     result.append(
        #         {
        #             "category": category,
        #             "total_persen_losses": losses,
        #             "total_nilai_losses": (losses / 100) * 1000,
        #             "data": calculated_data_by_category[category],
        #         }
        #     )
        

        return response(200, True, "Data retrieved successfully", result)

    @token_required
    @parse_params(
        Argument("is_bulk", location="args", type=int, required=False, default=0),
        Argument(
            "pareto_data", location="json", type=list, required=False, default=None
        ),
        Argument("detail_id", location="json", type=str, required=False),
        Argument("deviasi", location="json", required=False, type=float, default=None),
        Argument("persen_hr", location="json", required=False, type=float, default=None),
    )
    @Transactional(propagation=Propagation.REQUIRED)
    def put(self, user_id, transaction_id, is_bulk, pareto_data, **inputs):
        Cache.remove_by_prefix(f"data_calculated_data_by_category_{transaction_id}")
        
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
