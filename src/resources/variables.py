from typing import Set
from flask import Response
from flask_restful import Resource
from flask_restful.reqparse import Argument
from repositories.excels import ExcelsRepository
from utils import parse_params, response
from repositories import VariablesRepository
from utils.jwt_verif import token_required
from config import WINDOWS_EFFICIENCY_APP_API
from utils.util import fetch_data_from_api


class VariablesResource(Resource):
    """Variable resource"""

    @token_required
    def get(self, user_id: str, excel_id: str) -> Response:
        """Retrieve all variable from API based on EXCEL NAME"""
        excel = ExcelsRepository.get_by(id=excel_id).first()
        existing_variable_names = {
            var.input_name for var in VariablesRepository.get_by(excels_id=excel_id).all()}

        if excel:
            source_variables = fetch_data_from_api(
                f"{WINDOWS_EFFICIENCY_APP_API}/{excel.excel_filename}")

            [
                VariablesRepository.create(
                    excels_id=excel_id,
                    variable=variable.variabel,
                    satuan=variable.satuan,
                    variable_type=variable.type,
                    user_id=user_id
                )
                for variable in source_variables if variable.variabel not in existing_variable_names
            ]

        variables = VariablesRepository.get_by(excels_id=excel_id).all()

        # Outuput example
        # [
        #     {
        #         "type": "in",
        #         "unit": "bar",
        #         "variabel": "Site: Ambient pressure"
        #     },
        #     {
        #         "type": "in",
        #         "unit": "m",
        #         "variabel": "Site: Altitude"
        #     }]

        # res = {
        #     "data": [
        #         {
        #             "id": variable.id,
        #             "excels_id": variable.excels_id,
        #             "variable": variable.variable,
        #             "data_location": variable.data_location,
        #             "units": {
        #                 "id": variable.units.id,
        #                 "name": variable.units.unit,
        #                 # Add any other unit fields you need here
        #             },
        #             "base_case": variable.base_case,
        #             "variable_type": variable.variable_type,
        #         }
        #         for variable in variables
        #     ]
        # }

        return response(200, True, "Variables retrieved successfully", variables)


class VariableResource(Resource):

    @token_required
    def get(self, user_id: str, variable_id: str) -> Response:
        variable = VariablesRepository.get_by_id(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        return response(200, True, "Variable retrieved successfully", variable)

    @token_required
    def delete(self, user_id: str, variable_id: str) -> Response:
        """Delete a specific variable by id"""
        variable = VariablesRepository.get_by_id(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        VariablesRepository.delete(variable_id)

        return response(200, True, "Variable deleted successfully")
