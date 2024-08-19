from flask_restful import Resource
from flask_restful.reqparse import Argument
from utils import parse_params, response
from repositories import CaseInputsRepository


class CaseInputsResource(Resource):
    """CaseInputs"""

    def get(self):
        """Retrieve all variable"""
        case_inputs = CaseInputsRepository.get_by().all()

        res = {
            "data": [
                {
                    "id": case_input.id,
                    "cases_id": case_input.cases_id,
                    "variables_id": case_input.variables_id,
                    "data": case_input.data,
                }
                for case_input in case_inputs
            ]
        }

        return response(res, 200)
