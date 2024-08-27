from typing import Set
from flask import Response
from flask_restful import Resource
from flask_restful.reqparse import Argument
from repositories.excels import ExcelsRepository
from utils import parse_params, response
from repositories import VariablesRepository
from utils.jwt_verif import token_required
from config import config
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import Variable
from utils.util import fetch_data_from_api


class VariablesResource(Resource):
    """Variable resource"""

    # @token_required
    @parse_params(
        Argument("excel_id", location="args", required=True,
                 type=str, help="Excel Id is required"),
    )
    def get(self, excel_id: str) -> Response:
        """Retrieve all variable from API based on EXCEL NAME"""
        print(f"Get variables for excel {excel_id}")
        excel = ExcelsRepository.get_by(id=excel_id).first()

        if not excel:
            print(f"Excel {excel_id} not found")
            return response(404, False, "Excel not found")

        existing_variables = {
            var.excel_variable_name for var in VariablesRepository.get_by(excel_id=excel_id).all()
        }

        print(f"Existing variables: {existing_variables}")

        source_variables = fetch_data_from_api(
            f"{config.WINDOWS_EFFICIENCY_APP_API}/{excel.excel_filename}")

        if not source_variables:
            print(f"Failed to get variables from {excel.excel_filename}")
            return response(404, False, "Get VARIABLES failed")

        print(f"Source variables: {source_variables}")

        variable_records = []

        for variable in source_variables["data"]:
            new_var = Variable(
                excel_id=excel_id,
                input_name=variable["variabel"],
                satuan=variable["unit"],
                in_out=variable["type"],
                excel_variable_name=f"{variable['category']}: {variable['variabel']}",
                created_by="24d28102-4d6a-4628-9a70-665bcd50a0f0",
                category=variable["category"],
                short_name=None
            )
            new_var.is_pareto = True
            variable_records.append(new_var)

        db.session.add_all(variable_records)
        db.session.commit()

        response_data = [var.json for var in VariablesRepository.get_by(excel_id=excel_id, is_pareto=True).all()]

        return response(200, True, "Variables retrieved successfully", response_data)


class VariableResource(Resource):

    @token_required
    def get(self, user_id: str, variable_id: str) -> Response:
        variable = VariablesRepository.get_by_id(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        return response(200, True, "Variable retrieved successfully", variable.json)

    @token_required
    def delete(self, user_id: str, variable_id: str) -> Response:
        """Delete a specific variable by id"""
        variable = VariablesRepository.get_by_id(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        VariablesRepository.delete(variable_id)

        return response(200, True, "Variable deleted successfully")
