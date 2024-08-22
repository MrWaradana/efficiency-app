from flask_restful import Resource
from flask_restful.reqparse import Argument
from utils import parse_params, response
from repositories import CasesRepository
from utils.jwt_verif import token_required


class CasesResource(Resource):
    """Cases"""

    @token_required
    def get(self):
        """Retrieve all masterdata"""
        cases = CasesRepository.get_by().all()

        return response(200, True, "Cases retrieved successfully", cases)

    @token_required
    @parse_params(Argument("name", location="json", required=True))
    def post(self):
        """Create a new case"""
        case = CasesRepository.create()

        return response(201, True, "Case created successfully", case)

        # res = {
        #     "data": [
        #         {
        #             "id": case.id,
        #             "name": case.name
        #         }
        #         for case in cases
        #     ]
        # }

        # return response(res, 200)


class CaseResource(Resource):
    """Case"""

    @token_required
    def get(self, case_id):
        """Retrieve a specific case by id"""
        case = CasesRepository.get_by_id(case_id)

        if not case:
            return response(404, False, "Case not found")

        return response(200, True, "Case retrieved successfully", case)

    def delete(self, case_id):
        """Delete a specific case by id"""
        case = CasesRepository.get_by_id(case_id)

        if not case:
            return response(404, False, "Case not found")

        CasesRepository.delete(case)

        return response(200, True, "Case deleted successfully")

    # def put(self, case_id, **kwargs):
    #     """Update a specific case by id"""
    #     case = CasesRepository.get_by_id(case_id)

    #     if not case:
    #         return response(404, False, "Case not found")

    #     CasesRepository.update(case_id, **kwargs)

    #     return response(200, True, "Case updated successfully")
