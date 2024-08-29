from flask_restful import Resource
from flask_restful.reqparse import Argument

from schemas import CaseSchema
from utils import parse_params, response
from repositories import CasesRepository
from utils.jwt_verif import token_required
from digital_twin_migration.database import Transactional, Propagation

case_schema = CaseSchema()

class CasesResource(Resource):
    """
    Cases resource
    """

    @token_required
    def get(self, user_id):
        """
        Retrieve all masterdata

        :param user_id: User ID
        :return: Response with list of cases
        """
        cases = CasesRepository.get_by().all()
        
        return response(200, True, "Cases retrieved successfully", case_schema.dump(cases, many=True))

    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    @parse_params(Argument("name", location="json", required=True))
    def post(self, name, user_id):
        """
        Create a new case

        :param name: Name of the case
        :param user_id: User ID
        :return: Response with created case
        """
        case = CasesRepository.create(name=name)
        return response(201, True, "Case created successfully", case.json)


class CaseResource(Resource):
    """
    Case resource
    """

    @token_required
    def get(self, case_id, user_id):
        """
        Retrieve a specific case by id

        :param case_id: The id of the case to retrieve.
        :type case_id: int
        :param user_id: The id of the user.
        :type user_id: str
        :return: The response containing the case.
        :rtype: Response
        """
        case = CasesRepository.get_by_id(case_id)

        if not case:
            return response(404, False, "Case not found")

        return response(200, True, "Case retrieved successfully", case.json)

    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    def delete(self, case_id, user_id):
        """
        Delete a specific case by id

        :param case_id: The id of the case to delete.
        :type case_id: int
        :param user_id: The id of the user.
        :type user_id: str
        :return: The response containing the deleted case.
        :rtype: Response
        """
        case = CasesRepository.get_by_id(case_id)

        if not case:
            return response(404, False, "Case not found")

        case.delete()

        return response(200, True, "Case deleted successfully")

    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    @parse_params(Argument("name", location="json", required=False, default=None))
    def put(self, case_id, name, user_id):
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
        case = CasesRepository.get_by_id(case_id)

        if not case:
            return response(404, False, "Case not found")

        CasesRepository.update(case_id, name=name)

        return response(200, True, "Case updated successfully")
