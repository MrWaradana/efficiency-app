from flask_restful import Resource
from flask_restful.reqparse import Argument
from app.controllers.data import data_cost_benefit_controller, data_controller
from core.cache.cache_manager import Cache
from core.security import token_required
from core.utils import (parse_params, response)
from core.factory import data_detail_factory, variable_factory, data_factory

variable_schema = variable_factory.variable_schema
data_details_schema = data_detail_factory.data_detail_schema


class DataListCostBenefit(Resource):

    @token_required
    @parse_params(
        Argument("cost_threshold", location="args", type=int)
    )
    def get(self, user_id, cost_threshold, transaction_id):
        data = data_factory.data_repository.get_newest_data() if transaction_id == "new" else data_factory.data_repository.get_by_uuid(transaction_id)

        result, persen, nilai, total_biaya, total_cost_benefit, cost_threshold = data_cost_benefit_controller.get_cost_benefit_data(data.id, cost_threshold)

        return response(200, True, "Data retrieved successfully", {
            "cost_benefit_result": result,
            "total_cost_benefit": total_cost_benefit,
            "total_biaya": total_biaya,
            "total_persen": persen,
            "total_nilai": nilai,
            "cost_threshold": cost_threshold
        })
