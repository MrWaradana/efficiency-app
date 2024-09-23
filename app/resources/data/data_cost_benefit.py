from flask_restful import Resource
from flask_restful.reqparse import Argument
from app.controllers.data import data_pareto_controller, data_controller
from core.cache.cache_manager import Cache
from core.security import token_required
from core.utils import (parse_params, response)
from core.factory import data_detail_factory, variable_factory

variable_schema = variable_factory.variable_schema
data_details_schema = data_detail_factory.data_detail_schema


class DataListCostBenefit(Resource):

    @token_required
    def get(self, user_id):

        # Get newest transaction id
        data = data_controller.get_newest_data()

        result, _, _, _, _, total_cost_benefit = data_pareto_controller.get_data_pareto(
            data.id
        )

        return response(200, True, "Data retrieved successfully", {
            "cost_benefit_result": result,
            "total_cost_benefit": total_cost_benefit,
        })
