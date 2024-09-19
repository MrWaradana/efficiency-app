from digital_twin_migration.models.efficiency_app import EfficiencyDataDetail
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.controllers.data.data_details import data_detail_controller
from app.schemas import EfficiencyDataDetailSchema, VariableSchema
from core.security.jwt_verif import token_required
from core.utils import parse_params, response
from core.factory import data_detail_factory, variable_factory

variable_schema = variable_factory.variable_schema
data_details_schema = data_detail_factory.data_detail_schema


class DataDetailListResource(Resource):

    @token_required
    @parse_params(
        Argument("type", location="args", required=False, default="in"),
    )
    def get(self, user_id, transaction_id, type):
        """Get all transaction data by transaction id"""

        data_details = data_detail_controller.get_data_details(transaction_id, type)

        return response(
            200,
            True,
            "Data details retrieved successfully",
            data_details_schema.dump(data_details, many=True),
        )


class DataDetailResource(Resource):

    @token_required
    def get(self, user_id, transaction_id, detail_id):
        """Get transaction data by transaction id and variable id"""
        data_detail = data_detail_controller.get_data_detail(detail_id)

        return response(
            200,
            True,
            "Transaction data retrieved successfully",
            data_details_schema.dump(data_detail),
        )
