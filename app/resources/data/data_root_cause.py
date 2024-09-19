from collections import defaultdict
from uuid import UUID

from digital_twin_migration.database import Propagation, Transactional, db
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyDataDetailRootCause, EfficiencyTransaction,
    Variable, VariableCause)
from flask_restful import Resource
from flask_restful.reqparse import Argument
from sqlalchemy import and_, func

from app.controllers.data.data_details import data_detail_repository
from app.repositories.data_detail_root_cause import \
    DataDetailRootCauseRepository
from app.resources.data.data_details import data_details_schema
from app.resources.variable.variable import variable_repository
from app.resources.variable.variable_causes import (variable_cause_repository,
                                                    variable_cause_schema)
from app.schemas import (EfficiencyDataDetailRootCauseSchema,
                         EfficiencyDataDetailSchema, VariableSchema)
from core.security import token_required
from core.utils import calculate_gap, parse_params, response
from app.controllers.data import data_detail_root_cause_controller
from core.factory import variable_factory, data_detail_root_cause_factory

variable_schema = variable_factory.variable_schema
data_detail_root_cause_schema = data_detail_root_cause_factory.data_detail_root_cause_schema


class DataRootCausesListResource(Resource):
    @token_required
    def get(self, user_id, transaction_id, detail_id):

        root_causes = data_detail_root_cause_controller.get_by_detail_id(detail_id)

        return response(
            200,
            True,
            "Data root causes retrieved successfully",
            data_detail_root_cause_schema.dump(root_causes, many=True),
        )

    @token_required
    @parse_params(
        Argument("is_bulk", location="args", type=int, required=False, default=0),
        Argument(
            "data_root_causes", location="json", type=list, required=False, default=None
        ),
        Argument("cause_id", location="json", type=str, required=False, default=None),
        Argument("is_repair", location="json", type=str, required=False, default=False),
        Argument("biaya", location="json", type=float, required=False, default=None),
        Argument(
            "variable_header_value",
            location="json",
            type=dict,
            required=False,
            default=None,
        ),
    )
    def post(
        self, user_id, transaction_id, detail_id, is_bulk, data_root_causes, **inputs
    ):
        data = data_detail_root_cause_controller.create_data_detail_root_cause(user_id, transaction_id, detail_id, is_bulk, data_root_causes, **inputs)
        return response(200, True, "Data root cause created successfully")



