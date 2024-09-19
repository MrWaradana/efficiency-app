from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.controllers.data import data_trending_controller
from app.schemas import EfficiencyTransactionSchema, VariableSchema
from core.security.jwt_verif import token_required
from core.utils import parse_params, response

variable_schema = VariableSchema()
data_schema = EfficiencyTransactionSchema()


class DataTrendingListResource(Resource):
    @token_required
    @parse_params(
        Argument("variable_ids", location="args", type=str, required=True),
        Argument("start_date", location="args", type=str, required=False),
        Argument("end_date", location="args", type=str, required=False),
    )
    def get(self, user_id, variable_ids, start_date=None, end_date=None):
        data = data_trending_controller.get_trending_data(start_date, end_date, variable_ids)

        return response(200, True, "Data retrieved successfully", data)
