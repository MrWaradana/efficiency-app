from digital_twin_migration.models.efficiency_app import EfficiencyDataDetail
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.repositories import DataDetailRepository
from app.schemas import EfficiencyDataDetailSchema, VariableSchema
from core.security.jwt_verif import token_required
from core.utils import parse_params, response

variable_schema = VariableSchema()
data_details_schema = EfficiencyDataDetailSchema()
data_detail_repository = DataDetailRepository(EfficiencyDataDetail)


class DataDetailListResource(Resource):
    

    @token_required
    @parse_params(
        Argument("type", location="args", required=False, default="in"),
    )
    def get(self, user_id, transaction_id, type):
        """Get all transaction data by transaction id"""

        data_details = data_detail_repository.get_by_data_id_and_variable_type(
            transaction_id, type
        )

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

        data_detail = data_detail_repository.get_by_uuid(detail_id)

        if not data_detail:
            return response(404, False, "Data detail not found")

        return response(
            200,
            True,
            "Transaction data retrieved successfully",
            data_details_schema.dump(data_detail),
        )
