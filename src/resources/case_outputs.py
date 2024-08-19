from flask_restful import Resource
from flask_restful.reqparse import Argument
from utils import parse_params, response
from repositories import CaseOutputsRepository


class CaseOutputsResource(Resource):
    """CaseOutputs"""

    def get(self):
        """Retrieve all variable"""
        case_outputs = CaseOutputsRepository.get_by().all()

        res = {
            "data": [
                {
                    "id": case_output.id,
                    "cases_id": case_output.cases_id,
                    "variables_id": case_output.variables_id,
                    "data": case_output.data,
                }
                for case_output in case_outputs
            ]
        }

        return response(res, 200)
