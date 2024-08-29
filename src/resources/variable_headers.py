
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


Variable_header_schema = VariableHeaderSchema()

class VariableHeadersResource(Resource):

    @token_required
    def get(self, variable_id: str, user_id: str) -> Response:
        variable = VariablesRepository.get_by_id(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        headers = variable.headers

        return response(200, True, "Variable headers retrieved successfully", Variable_header_schema.dump(headers, many=True))

    @token_required
    @parse_params(
        Argument(
            "name",
            location="json",
            required=True,
            type=str,
            help="Name of the header is required",
        ),
    )
    def post(self, variable_id: str, user_id: str, **inputs) -> Response:
        variable = VariablesRepository.get_by_id(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        header = HeadersRepository.create(**inputs, variable_id=variable_id, created_by=user_id)

        return response(201, True, "Header created successfully", Variable_header_schema.dump(header))


class VariableHeaderResource(Resource):

    @token_required
    def get(self, variable_id: str, header_id: str, user_id) -> Response:
        header = HeadersRepository.get_by_id(header_id)

        if not header or str(header.variable_id) != variable_id:
            return response(404, False, "Header not found")

        return response(200, True, "Header retrieved successfully", Variable_header_schema.dump(header))

    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    def delete(self, variable_id: str, header_id: str, user_id) -> Response:
        header = HeadersRepository.get_by_id(header_id)

        if not header:
            return response(404, False, "Header not found")

        header.delete()

        return response(200, True, "Header deleted successfully")

    @token_required
    @parse_params(
        Argument("name", location="json", required=False, default=None),
    )
    @Transactional(propagation=Propagation.REQUIRED)
    def put(self, variable_id: str, header_id: str, user_id, **attributes) -> Response:
        header = HeadersRepository.get_by_id(header_id)

        if not header:
            return response(404, False, "Header not found")

        HeadersRepository.update(header_id, **attributes, updated_by=user_id)

        return response(200, True, "Header updated successfully")
