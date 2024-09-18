from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import VariableCause
from flask import Response
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.repositories import CausesRepository
from app.resources.variable.variable import variable_repository
from app.schemas import VariableCauseSchema
from core.security import token_required
from core.utils import parse_params, response

variable_cause_schema = VariableCauseSchema()
variable_cause_repository = CausesRepository(VariableCause)


class VariableCausesResource(Resource):

    @token_required
    def get(
        self,
        variable_id: str,
        user_id: str,
    ) -> Response:
        variable = variable_repository.get_by_uuid(variable_id)
        if not variable:
            return response(404, False, "Variable not found")

        causes = variable_cause_repository.get_by_variable_id(variable_id, {"children"})

        return response(
            200,
            True,
            "Variable causes retrieved successfully",
            variable_cause_schema.dump(causes, many=True),
        )

    @token_required
    @parse_params(
        Argument(
            "name",
            location="json",
            required=True,
            type=str,
            help="Name of the cause is required",
        ),
        Argument("parent_id", location="json", required=False, type=str, default=None),
    )
    def post(self, variable_id: str, user_id: str, **inputs) -> Response:
        variable = variable_repository.get_by_uuid(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        cause = variable_cause_repository.create(
            {"created_by": user_id, "variable_id": variable_id, **inputs}
        )

        return response(
            200, True, "Cause created successfully", variable_cause_schema.dump(cause)
        )


class VariableCauseResource(Resource):

    @token_required
    def get(self, variable_id: str, cause_id: str, user_id) -> Response:
        cause = variable_cause_repository.get_by_uuid(cause_id)

        if not cause:
            return response(404, False, "Cause not found")

        return response(
            200, True, "Cause retrieved successfully", variable_cause_schema.dump(cause)
        )

    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    def delete(self, variable_id: str, cause_id: str, user_id) -> Response:
        cause = variable_cause_repository.get_by_uuid(cause_id)

        if not cause:
            return response(404, False, "Cause not found")

        variable_cause_repository.delete(cause)
        return response(200, True, "Cause deleted successfully")

    @token_required
    @parse_params(
        Argument("name", location="json", required=False, default=None),
    )
    @Transactional(propagation=Propagation.REQUIRED)
    def put(
        self, variable_id: str, cause_id: str, user_id: str, **attributes
    ) -> Response:
        cause = variable_cause_repository.get_by_uuid(cause_id)

        if not cause:
            return response(404, False, "Cause not found")

        variable_cause_repository.update(cause, {"updated_by": user_id, **attributes})

        return response(200, True, "Cause updated successfully")
