

from flask import Response
from flask_restful import Resource

from core.security.jwt_verif import token_required
from core.factory.data import data_factory
from app.controllers.data import data_nphr_controller
from core.utils import response


class DataNPHRResource(Resource):
    @token_required
    def get(
        self,
        user_id: str,
        data_id: str = None,
    ) -> Response:
        data_id = None if data_id == "null" else data_id

        (nphr,
         result_chart,
         data_id,
         data_name,
         result_pareto,
         total_persen,
         total_losses,
         total_biaya,
         total_cost_benefit) = data_nphr_controller.get_data_nphr(data_id)

        return response(
            200,
            True,
            "Data retrieved successfully",
            {
                "name": data_name,
                "data_id": data_id,
                "chart_result": result_chart,
                "nphr_result": nphr,
                "pareto_result": result_pareto,
                "total_persen": total_persen,
                "total_nilai": total_losses,
                "total_cost_gap": total_biaya,
                "total_cost_benefit": total_cost_benefit,
            }
        )
