from flask_restful import Resource
from flask_restful.reqparse import Argument
from utils import parse_params, response
from repositories import CasesRepository


class CasesResource(Resource):
    """Cases"""

    def get(self):
        """Retrieve all variable"""
        cases = CasesRepository.get_by().all()

        res = {
            "data": [
                {
                    "id": case.id,
                    "name": case.name
                }
                for case in cases
            ]
        }

        return response(res, 200)
