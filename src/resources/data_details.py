from collections import defaultdict
from flask_restful import Resource
from flask_restful.reqparse import Argument
from sqlalchemy import and_
from schemas import VariableSchema, EfficiencyDataDetailSchema
from utils import (
    parse_params,
    response,
    calculate_gap,
    calculate_nilai_losses,
)
from repositories import VariablesRepository, TransactionRepository
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail,
    EfficiencyTransaction,
    Variable,
)

from digital_twin_migration.database import db

from utils.jwt_verif import token_required

variable_schema = VariableSchema()
data_details_schema = EfficiencyDataDetailSchema()


class TransactionDataDetailsResource(Resource):

    @token_required
    @parse_params(
        Argument("type", location="args", required=False, default="in"),
    )
    def get(self, user_id, transaction_id, type):
        """Get all transaction data by transaction id"""

        data_details = (
            EfficiencyDataDetail.query.join(EfficiencyDataDetail.efficiency_transaction)
            .join(EfficiencyDataDetail.variable)
            .filter(
                and_(
                    EfficiencyDataDetail.efficiency_transaction_id == transaction_id, Variable.in_out == type
                )
            )
            .all()
        )

        return response(200, True, "Data details retrieved successfully", data_details_schema.dump(data_details, many=True))


class TransactionDataDetailResource(Resource):

    @token_required
    def get(self, user_id, transaction_id):
        """Get transaction data by transaction id and variable id"""

        data_detail = EfficiencyDataDetail.query.join(EfficiencyDataDetail.efficiency_transaction).filter(and_(EfficiencyDataDetail.efficiency_transaction_id == transaction_id)).first()

        return response(200, True, "Transaction data retrieved successfully", data_details_schema.dump(data_detail))


class TransactionDataParetoResource(Resource):

    @token_required
    def get(self, user_id, transaction_id):
        current_data = EfficiencyDataDetail.query.join(EfficiencyDataDetail.efficiency_transaction).join(EfficiencyDataDetail.variable).filter(
                and_(
                    EfficiencyTransaction.id == transaction_id,
                    Variable.in_out == "out"
                )
            ).all()
        

        target_data = EfficiencyDataDetail.query.join(EfficiencyDataDetail.efficiency_transaction).join(EfficiencyDataDetail.variable).filter(
                and_(
                    EfficiencyTransaction.jenis_parameter == "Target",
                    Variable.in_out == "out",
                )
            ).all()
        

        current_dict = {item.variable_id: item for item in current_data}
        target_dict = {item.variable_id: item for item in target_data}

        calculated_data = []
        aggregated_nilai_losses = defaultdict(float)
        
    
        for variable_id, current_item in current_dict.items():
            target_item = target_dict.get(variable_id)


            
            if target_item:
                gap = calculate_gap(target_item.nilai, current_item.nilai)

                if gap is None:
                    raise Exception(gap, target_item.nilai_string, current_item.nilai)

                nilai_losses = calculate_nilai_losses(
                    gap, current_item.deviasi, current_item.persen_hr
                )

                aggregated_nilai_losses[current_item.variable.category] += (
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
                        "nilai_losses": nilai_losses,
                        "gap": gap,
                    }
                )
        

        
        result = []
        for category, losses in aggregated_nilai_losses.items():
            category_data = {
                "category": category,
                "total_losses": losses,
                "data": [
                    item
                    for item in calculated_data
                    if item["variable"]["category"] == category
                ],
            }

            result.append(category_data)
        


        data_sorted = sorted(result, key=lambda x: x["total_losses"], reverse=True)

        return response(200, True, "Data retrieved successfully", data_sorted)
