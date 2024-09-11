from digital_twin_migration.models.efficiency_app import EfficiencyDataDetail
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.repositories import DataDetailRepository
from app.schemas import EfficiencyDataDetailSchema, VariableSchema, EfficiencyTransactionSchema
from core.security.jwt_verif import token_required
from core.utils import parse_params, response
from app.controllers import data_controller

variable_schema = VariableSchema()
data_schema = EfficiencyTransactionSchema()


class DataTrendingListResource(Resource):
    @token_required
    @parse_params(
        Argument("variable_id", location="args", type=str, required=True),
        Argument("start_date", location="args", type=str, required=False),
        Argument("end_date", location="args", type=str, required=False),
    )
    def get(self, user_id, variable_id, start_date=None, end_date=None):
        data = data_controller.get_data_trending(start_date, end_date, variable_id)

        return response(200, True, "Data retrieved successfully", data)
