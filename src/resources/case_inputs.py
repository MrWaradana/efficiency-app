from flask import request
from flask_restful import Resource
from flask_restful.reqparse import Argument
from utils import parse_params, response
from repositories import CaseInputsRepository, CasesRepository, VariablesRepository
from sqlalchemy.exc import SQLAlchemyError


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

    def post(self):
        # cases = CasesRepository.get_by(cases_id)
        # [
        # {
        #     XXXXXXXX123 : 123123123
        # }
        # ]
        case = CasesRepository.create()
        try:
            # case.commit()

            input_data = request.get_json()
            # [
            # {
            #     XXXXXXXX123 : 123123123
            # }
            # ]
            # while case is None or case.id is None:
            #     case = CasesRepository.create()

            for key, value in input_data.items():
                CaseInputsRepository.create(case.id, key, value)

            # commit the create case data
            case.commit()
        except SQLAlchemyError as e:
            case.rollback()
        except Exception as e:
            # Catch any other exceptions
            case.rollback()

        res = {"data": input_data}

        return response(res, 200)
