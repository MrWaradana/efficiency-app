from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import VariableHeader
from flask import Response
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.repositories.headers import HeadersRepository
from app.resources.variable.main import variable_repository
from app.schemas.variable import VariableHeaderSchema
from core.security.jwt_verif import token_required
from core.utils import parse_params, response

variable_header_schema = VariableHeaderSchema()
variable_header_repository = HeadersRepository(VariableHeader)


class VariableHeadersResource(Resource):

    @token_required
    def get(self, variable_id: str, user_id: str) -> Response:
        variable = variable_repository.get_by_uuid(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        headers = variable_header_repository.get_by_variable_id(
            variable_id, {"variable"}
        )

        return response(
            200,
            True,
            "Variable headers retrieved successfully",
            variable_header_schema.dump(headers, many=True),
        )

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
        variable = variable_repository.get_by_uuid(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        header = variable_header_repository.create(
            {**inputs, "variable_id": variable_id, "created_by": user_id}
        )

        return response(
            201,
            True,
            "Header created successfully",
            variable_header_schema.exclude("variable").dump(header),
        )


class VariableHeaderResource(Resource):

    @token_required
    def get(self, variable_id: str, header_id: str, user_id) -> Response:
        header = variable_header_repository.get_by_uuid(header_id)

        if not header:
            return response(404, False, "Header not found")


        return response(
            200,
            True,
            "Header retrieved successfully",
            variable_header_schema.dump(header),
        )

    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    def delete(self, variable_id: str, header_id: str, user_id) -> Response:
        header = variable_header_repository.get_by_uuid(header_id)

        if not header:
            return response(404, False, "Header not found")

        variable_header_repository.delete(header)

        return response(200, True, "Header deleted successfully")

    @token_required
    @parse_params(
        Argument("name", location="json", required=False, default=None),
    )
    @Transactional(propagation=Propagation.REQUIRED)
    def put(self, variable_id: str, header_id: str, user_id, **attributes) -> Response:
        header = variable_header_repository.get_by_uuid(header_id)

        if not header:
            return response(404, False, "Header not found")

        variable_header_repository.update(header, {**attributes, "updated_by": user_id})

        return response(200, True, "Header updated successfully")
