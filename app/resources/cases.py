from functools import partial

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import Case
from flask import Response
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.repositories import CasesRepository
from app.schemas import CaseSchema
from core.security import token_required
from core.utils import parse_params, response

case_repository = CasesRepository(Case)
case_schema = CaseSchema()


class CasesResource(Resource):
    @token_required
    def get(self, user_id: str) -> Response:
        """Get all cases from the database.

        Args:
            user_id (str): The id of the user.

        Returns:
            Response: A response containing the cases.
        """
        # Query the Cases table in the database and retrieve all cases
        cases = case_repository.get_all()

        # Return a response containing the cases
        return response(
            200,
            True,
            "Cases retrieved successfully",
            case_schema.dump(cases, many=True),
        )

    @token_required
    @parse_params(Argument("name", location="json", required=True))
    def post(self, name: str, user_id: str) -> Response:
        is_case = case_repository.get_by_name(name)

        if is_case:
            return response(409, False, "Case already exists")

        case = case_repository.create({"name": name})
        return response(201, True, "Case created successfully", case_schema.dump(case))


class CaseResource(Resource):
    @token_required
    def get(self, case_id: str, user_id: str) -> Response:
        case = case_repository.get_by_uuid(case_id)

        if not case:
            return response(404, False, "Case not found")

        return response(
            200, True, "Case retrieved successfully", case_schema.dump(case)
        )

    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    def delete(self, case_id, user_id) -> Response:
        case = case_repository.get_by_uuid(case_id)

        if not case:
            return response(404, False, "Case not found")

        case_repository.delete(case)

        return response(200, True, "Case deleted successfully")

    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    @parse_params(Argument("name", location="json", required=False, default=None))
    def put(self, case_id, user_id, **attributes):
        """
        Update a specific case by id

        :param case_id: The id of the case to update.
        :type case_id: int
        :param name: The new name of the case.
        :type name: str
        :param user_id: The id of the user.
        :type user_id: str
        :return: The response containing the updated case.
        :rtype: Response
        """
        case = case_repository.get_by_uuid(case_id)

        if not case:
            return response(404, False, "Case not found")

        case_repository.update(case, attributes)

        return response(200, True, "Case updated successfully")
