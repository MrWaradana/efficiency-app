from collections import defaultdict
from uuid import UUID

from digital_twin_migration.database import Propagation, Transactional, db
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyDataDetailRootCause, EfficiencyTransaction,
    Variable, VariableCause)
from flask_restful import Resource
from flask_restful.reqparse import Argument
from sqlalchemy import and_, func

from app.controllers.data.data_detail import data_detail_repository
from app.repositories.data_detail_root_cause import \
    DataDetailRootCauseRepository
from app.resources.data.data_details import data_details_schema
from app.resources.variable.main import variable_repository
from app.resources.variable.variable_causes import (variable_cause_repository,
                                                    variable_cause_schema)
from app.schemas import (EfficiencyDataDetailRootCauseSchema,
                         EfficiencyDataDetailSchema, VariableSchema)
from core.security import token_required
from core.utils import calculate_gap, parse_params, response

variable_schema = VariableSchema()
data_detail_root_cause_schema = EfficiencyDataDetailRootCauseSchema()
data_detail_root_cause_repository = DataDetailRootCauseRepository(
    EfficiencyDataDetailRootCause
)


class DataRootCausesListResource(Resource):
    @token_required
    def get(self, user_id, transaction_id, detail_id):
        # variable_id = data_detail_repository.get_by_uuid(detail_id).variable_id

        # causes = variable_cause_repository.get_by_variable_id(
        #     variable_id, {"children", "root_causes"}
        # )
        # result = [process_root_causes(cause, UUID(detail_id)) for cause in causes]

        root_causes = data_detail_root_cause_repository.get_by_detail_id(detail_id)

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
    @Transactional(propagation=Propagation.REQUIRED)
    def post(
        self, user_id, transaction_id, detail_id, is_bulk, data_root_causes, **inputs
    ):
        if is_bulk:
            if not data_root_causes:
                return response(
                    400, False, "data_root_causes is required when 'is_bulk' is set"
                )
            # Check if data with cause_id already exists
            # Step 1: Collect all root cause IDs to delete
            root_cause_ids = [root_cause["cause_id"] for root_cause in data_root_causes]

            # Step 2: Fetch all records to delete in a single query
            data_roots = data_detail_root_cause_repository.get_by_detail_id_cause_ids(
                root_cause_ids, detail_id
            )

            if data_roots:
                # Step 3: Delete all records
                data_detail_root_cause_repository.delete_bulk(data_roots)

            data_root_causes_records = [
                EfficiencyDataDetailRootCause(
                    data_detail_id=detail_id,
                    cause_id=root_cause["cause_id"],
                    is_repair=(
                        root_cause["is_repair"] if "is_repair" in root_cause else False
                    ),
                    biaya=root_cause["biaya"] if "biaya" in root_cause else 0,
                    variable_header_value=(
                        root_cause["variable_header_value"]
                        if "variable_header_value" in root_cause
                        else None
                    ),
                    created_by=user_id,
                )
                for root_cause in data_root_causes
            ]

            data_detail_root_cause_repository.create_bulk(data_root_causes_records)

        else:
            missing_input = next(
                (name for name, input in inputs.items() if not input), None
            )
            if missing_input:
                return response(
                    400,
                    False,
                    f"'{missing_input}' is required when 'is_bulk' is not set",
                )

            data_detail_root_cause_repository.create(
                {**inputs, "data_detail_id": detail_id, "created_by": user_id}
            )

        return response(200, True, "Data root cause created successfully")


def process_root_causes(cause, detail_id):
    # Create the node dictionary with the dumped cause data
    node_dict = {
        **variable_cause_schema.dump(cause),
        "children": [],
        "root_causes": [
            data_detail_root_cause_schema.dump(root_cause)
            for root_cause in cause.root_causes
            if root_cause.data_detail_id == detail_id
        ],
    }

    # Recursively process children
    node_dict["children"] = [
        process_root_causes(child, detail_id) for child in cause.children
    ]

    return node_dict
