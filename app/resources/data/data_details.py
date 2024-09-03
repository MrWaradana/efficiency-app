from collections import defaultdict

from digital_twin_migration.database import Propagation, Transactional, db
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyDataDetailRootCause, EfficiencyTransaction,
    Variable)
from flask_restful import Resource
from flask_restful.reqparse import Argument
from repositories import TransactionRepository, VariablesRepository
from schemas import EfficiencyDataDetailSchema, VariableSchema
from sqlalchemy import and_
from utils import calculate_gap, calculate_nilai_losses, parse_params, response
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
                    EfficiencyDataDetail.efficiency_transaction_id == transaction_id,
                    Variable.in_out == type,
                )
            )
            .all()
        )

        return response(
            200,
            True,
            "Data details retrieved successfully",
            data_details_schema.dump(data_details, many=True),
        )


class TransactionDataDetailResource(Resource):

    @token_required
    def get(self, user_id, transaction_id, detail_id):
        """Get transaction data by transaction id and variable id"""

        data_detail = EfficiencyDataDetail.query.get(detail_id)

        return response(
            200,
            True,
            "Transaction data retrieved successfully",
            data_details_schema.dump(data_detail),
        )
