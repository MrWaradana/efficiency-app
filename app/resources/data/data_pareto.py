from collections import defaultdict

from digital_twin_migration.database import Propagation, Transactional, db
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyDataDetailRootCause, EfficiencyTransaction,
    Variable)
from flask_restful import Resource
from flask_restful.reqparse import Argument
from schemas import EfficiencyDataDetailSchema, VariableSchema
from sqlalchemy import and_, func
from utils import (calculate_gap, calculate_persen_losses, parse_params,
                   response)
from utils.jwt_verif import token_required

variable_schema = VariableSchema()
data_details_schema = EfficiencyDataDetailSchema()


class TransactionListDataParetoResource(Resource):

    @token_required
    def get(self, user_id, transaction_id):
        current_data = (
            db.session.query(EfficiencyDataDetail, EfficiencyDataDetail.total_cost())
            .join(EfficiencyDataDetail.efficiency_transaction)
            .join(EfficiencyDataDetail.variable)
            .filter(
                and_(
                    EfficiencyTransaction.id == transaction_id, Variable.in_out == "out"
                )
            )
            .all()
        )

        target_data = (
            EfficiencyDataDetail.query.join(EfficiencyDataDetail.efficiency_transaction)
            .join(EfficiencyDataDetail.variable)
            .filter(
                and_(
                    EfficiencyTransaction.jenis_parameter == "Target",
                    Variable.in_out == "out",
                )
            )
            .all()
        )

        current_dict = {
            item.variable_id: (item, total_cost) for item, total_cost in current_data
        }
        target_dict = {item.variable_id: item for item in target_data}

        calculated_data = []
        aggregated_nilai_losses = defaultdict(float)

        for variable_id, current_item in current_dict.items():
            target_item = target_dict.get(variable_id)
            data_item = current_item[0]

            if target_item:
                gap = calculate_gap(target_item.nilai, data_item.nilai)

                if gap is None:
                    raise Exception(gap, target_item.nilai_string, data_item.nilai)

                persen_losses = calculate_persen_losses(
                    gap, data_item.deviasi, data_item.persen_hr
                )

                nilai_losses = (persen_losses / 100) * 1000

                aggregated_nilai_losses[data_item.variable.category] += (
                    nilai_losses if nilai_losses is not None else 0
                )

                calculated_data.append(
                    {
                        "id": data_item.id,
                        "variable": variable_schema.dump(data_item.variable),
                        "existing_data": data_item.nilai,
                        "reference_data": target_item.nilai,
                        "deviasi": data_item.deviasi,
                        "persen_hr": data_item.persen_hr,
                        "persen_losses": persen_losses,
                        "nilai_losses": nilai_losses,
                        "gap": gap,
                        "total_biaya": current_item[1],
                    }
                )

        result = []
        for category, losses in aggregated_nilai_losses.items():
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

            result.append(category_data)

        data_sorted = sorted(
            result, key=lambda x: x["total_nilai_losses"], reverse=True
        )

        return response(200, True, "Data retrieved successfully", data_sorted)


class TransactionDetailDataParetoResource(Resource):
    @token_required
    @parse_params(
        Argument("deviasi", location="json", required=True, type=float),
        Argument("persen_hr", location="json", required=True, type=float),
    )
    @Transactional(propagation=Propagation.REQUIRED)
    def put(user_id, transaction_id, deviasi, persen_hr, detail_id):

        data_detail = EfficiencyDataDetail.query.get(detail_id)
        data_detail.devisi = deviasi
        data_detail.persen_hr = persen_hr
        data_detail.updated_by = user_id

        return response(200, True, "Data Detail updated successfully")
