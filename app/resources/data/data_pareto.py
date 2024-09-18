import math
from collections import defaultdict

from digital_twin_migration.database import Propagation, Transactional
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.controllers.data.data_detail import (data_detail_controller,
                                              data_detail_repository)
from app.schemas import EfficiencyDataDetailSchema, VariableSchema
from core.cache.cache_manager import Cache
from core.security import token_required
from core.utils import (parse_params, response)

variable_schema = VariableSchema()
data_details_schema = EfficiencyDataDetailSchema()


# This class likely represents a resource for handling data lists with Pareto analysis functionality.
# This class likely represents a resource for handling data lists with Pareto analysis functionality.
class DataListParetoResource(Resource):

    @token_required
    @parse_params(
        Argument(
            "percent_threshold", location="args", type=int, required=False, default=None
        ),
    )
    def get(self, user_id, transaction_id, percent_threshold):

        result, total_persen, total_losses, percent_threshold = data_detail_controller.get_data_pareto(
            transaction_id, percent_threshold
        )


        return response(200, True, "Data retrieved successfully", {
            "pareto_result": result,
            "total_persen": total_persen,
            "total_nilai": total_losses,
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
    @Transactional(propagation=Propagation.REQUIRED)
    def put(self, user_id, transaction_id, is_bulk, pareto_data, **inputs):
        Cache.remove_by_prefix(f"data_calculated_data_by_category_{transaction_id}")

        if is_bulk:
            if not pareto_data:
                return response(
                    400, False, "pareto_data is required when 'is_bulk' is set"
                )

            for pareto in pareto_data:
                data_detail = data_detail_repository.get_by_uuid(pareto["detail_id"])
                if not data_detail:
                    return response(404, False, "Data Detail not found")
                data_detail_repository.update(
                    data_detail,
                    {
                        "deviasi": (
                            pareto["deviasi"]
                            if "deviasi" in pareto
                            else data_detail.deviasi
                        ),
                        "persen_hr": (
                            pareto["persen_hr"]
                            if "persen_hr" in pareto
                            else data_detail.persen_hr
                        ),
                        "updated_by": user_id,
                    },
                )

        else:
            data_detail = data_detail_repository.get_by_uuid(inputs["detail_id"])
            if not data_detail:
                return response(404, False, "Data Detail not found")

            data_detail_repository.update(
                data_detail,
                {
                    "deviasi": (
                        inputs["deviasi"]
                        if "deviasi" in inputs
                        else data_detail.deviasi
                    ),
                    "persen_hr": (
                        inputs["persen_hr"]
                        if "persen_hr" in inputs
                        else data_detail.persen_hr
                    ),
                    "updated_by": user_id,
                },
            )

        return response(200, True, "Data Detail updated successfully")
