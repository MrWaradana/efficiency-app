from flask import request
from flask_restful import Resource
from flask_restful.reqparse import Argument
import requests
from config import WINDOWS_EFFICIENCY_APP_API
from utils import parse_params, response, get_key_by_value
from repositories import CasesRepository, VariablesRepository, TransactionRepository
from sqlalchemy.exc import SQLAlchemyError
from digital_twin_migration.models import EfficiencyTransaction, db

from utils.jwt_verif import token_required


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

    @parse_params(Argument("periode", location="json", required=True, type=str),
                  Argument("jenis_parameter", location="json", required=True, type=str),
                  Argument("excel_id", location="json", required=True, type=str),
                  Argument("inputs", location="json", required=True, type=dict),
                  )
    @token_required
    def post(self, user_id, periode, jenis_parameter, excel_id, inputs):
        # try:
        #     # case.commit()
        #     # input_data = request.get_json()
        #     # [
        #     # {
        #     #     XXXXXXXX123 : 123123123
        #     # }
        #     # ]
        #     # while case is None or case.id is None:
        #     #     case = CasesRepository.create()

        #     input_data = {}

        #     for key, value in inputs.items():
        #         variable_input = VariablesRepository.get_by_id(key).input_name
        #         input_data[variable_input] = value

        #         TransactionRepository.create(
        #             periode=periode,
        #             jenis_parameter=jenis_parameter,
        #             excel_id=excel_id,
        #             variable_id=key,
        #             nilai=value,
        #             created_by=user_id
        #         )

        #     # Send data to API Excel
        #     response = requests.post(WINDOWS_EFFICIENCY_APP_API, json=input_data)

        #     # # for key, value in input_data.items():
        #     # #     CaseInputsRepository.create(case.id, key, value)

        #     # # commit the create case data
        #     # case.commit()
        # except SQLAlchemyError as e:
        #     case.rollback()
        # except Exception as e:
        #     # Catch any other exceptions
        #     case.rollback()

        variable_mappings = {
            var.id: var.input_name for var in VariablesRepository.get_by(excel_id=excel_id).all()}
        input_data = {}
        transaction_records = []

        for key, value in inputs.items():
            variable_input = variable_mappings.get(key)
            input_data[variable_input] = value

            transaction_records.append(EfficiencyTransaction(
                periode=periode,
                jenis_parameter=jenis_parameter,
                excel_id=excel_id,
                variable_id=key,
                nilai=value,
                created_by=user_id
            ))

        # TransactionRepository.bulk_create(transaction_records)

        # Send data to API
        try:
            res = requests.post(WINDOWS_EFFICIENCY_APP_API, json=input_data)
            res.raise_for_status()  # Raises an error for HTTP codes 4xx/5xx
        except requests.exceptions.RequestException as e:
            # Handle error, e.g., logging or retry mechanism
            print(f"API request failed: {e}")
            return response(500, False, "Failed to create transaction")

        outputs = res.json()

        for variable_title, input_value in outputs.items():
            variable_id = get_key_by_value(variable_mappings, variable_title)

            transaction_records.append(EfficiencyTransaction(
                periode=periode,
                jenis_parameter=jenis_parameter,
                excel_id=excel_id,
                variable_id=variable_id,
                nilai=input_value,
                created_by=user_id
            ))

        try:
            db.session.bulk_save_objects(transaction_records)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return response(500, False, "Failed to create transaction")

        return response(200, True, "Transaction created successfully")
