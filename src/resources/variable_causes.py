from flask import Response
from flask_restful import Resource
from flask_restful.reqparse import Argument
from sqlalchemy import and_
from repositories.excels import ExcelsRepository
from repositories.causes import CausesRepository
from repositories.headers import HeadersRepository
from schemas.variable import VariableCauseSchema, VariableHeaderSchema, VariableSchema
from utils import parse_params, response
from repositories import VariablesRepository
from utils.jwt_verif import token_required
from config import config
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import Variable, VariableCause
from utils.util import fetch_data_from_api

from digital_twin_migration.database import Transactional, Propagation

variable_cause_schema = VariableCauseSchema()

class VariableCausesResource(Resource):

    @token_required
    def get(
        self,
        variable_id: str,
        user_id: str,
    ) -> Response:
        variable = VariablesRepository.get_by(id=variable_id).first()

        if not variable:
            return response(404, False, "Variable not found")

        causes = VariableCause.query.filter(
            and_(
                VariableCause.variable_id == variable_id,
                VariableCause.parent_id.is_(None),
            )
            ).all()
        

        return response(200, True, "Variable causes retrieved successfully", variable_cause_schema.dump(causes, many=True))

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
        variable = VariablesRepository.get_by_id(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        cause = CausesRepository.create(**inputs, created_by=user_id, variable_id=variable_id)

        return response(200, True, "Cause created successfully", variable_cause_schema.dump(cause))


class VariableCauseResource(Resource):

    @token_required
    def get(self, variable_id: str, cause_id: str, user_id) -> Response:
        cause = CausesRepository.get_by(id=cause_id).first()

        if not cause:
            return response(404, False, "Cause not found")

        return response(200, True, "Cause retrieved successfully", variable_cause_schema.dump(cause))

    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    def delete(self, variable_id: str, cause_id: str, user_id) -> Response:
        cause = CausesRepository.get_by_id(cause_id)

        if not cause:
            return response(404, False, "Cause not found")

        cause.delete()
        return response(200, True, "Cause deleted successfully")

    @token_required
    @parse_params(
        Argument("name", location="json", required=False, default=None),
    )
    @Transactional(propagation=Propagation.REQUIRED)
    def put(self, variable_id: str, cause_id: str, **attributes) -> Response:
        cause = CausesRepository.get_by_id(cause_id)

        if not cause:
            return response(404, False, "Cause not found")

        CausesRepository.update(cause_id, **attributes)

        return response(200, True, "Cause updated successfully")



