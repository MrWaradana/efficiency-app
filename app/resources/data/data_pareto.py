from flask_restful import Resource
from flask_restful.reqparse import Argument
from app.controllers.data.data_pareto import data_pareto_controller
from core.cache.cache_manager import Cache
from core.security import token_required
from core.utils import (parse_params, response)
from core.factory import data_detail_factory, variable_factory

variable_schema = variable_factory.variable_schema
data_details_schema = data_detail_factory.data_detail_schema


class DataListParetoResource(Resource):

    @token_required
    @parse_params(
        Argument(
            "percent_threshold", location="args", type=int, required=False, default=None,
        ),
    )
    def get(self, user_id, transaction_id, percent_threshold):
        
        result_pareto, result_chart, total_persen, total_losses, total_biaya, total_cost_benefit = data_pareto_controller.get_data_pareto(
            transaction_id, percent_threshold
        )

        return response(200, True, "Data retrieved successfully", {
            "pareto_result": result_pareto,
            "chart_result": result_chart,
            "total_persen": total_persen,
            "total_nilai": total_losses,
            "total_cost_gap": total_biaya,
            "total_cost_benefit": total_cost_benefit,
            "percent_threshold": percent_threshold,
        })

    @token_required
    @parse_params(
        Argument("is_bulk", location="args", type=int, required=False, default=0),
        Argument(
            "pareto_data", location="json", type=list, required=False, default=None
        ),
        Argument("detail_id", location="json", type=str, required=False),
        Argument("deviasi", location="json", required=False, type=float, default=None),
        Argument(
            "persen_hr", location="json", required=False, type=float, default=None
        ),
    )
    def put(self, user_id, transaction_id, is_bulk, pareto_data, **inputs):

        result = data_pareto_controller.update_pareto(user_id, transaction_id, is_bulk, pareto_data, **inputs)

        return response(200, True, "Data Detail updated successfully", result if result else None)
