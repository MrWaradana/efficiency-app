import random

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import (Variable,
                                                          VariableCause)
from flask import Response, request
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.repositories import VariablesRepository
from app.controllers.excels import excel_repository
from app.schemas import (VariableCauseSchema, VariableHeaderSchema,
                         VariableSchema)
from core.config import config
from core.security.jwt_verif import token_required
from core.utils import parse_params, response
from core.utils.util import fetch_data_from_api
import requests
from werkzeug import exceptions
variable_schema = VariableSchema()
variable_repository = VariablesRepository(Variable)


class VariablesResource(Resource):
    @token_required
    @parse_params(
        Argument(
            "excel_id",
            location="args",
            required=True,
            type=str,
            help="Excel Id is required",
        ),
        Argument("type", location="args", required=False, type=str, default="in"),
    )
    def get(self, excel_id: str, type: str, user_id) -> Response:
        """Retrieve all variable from API based on EXCEL NAME"""

        # Cek Koneksi Ke PI Server
        is_connected_to_pi = False
        
        # Define your credentials
        # Define your credentials
        username = 'tjb.piwebapi'
        password = 'PLNJepara@2024'
        
        try:
            res = requests.get(f"https://10.47.0.54/piwebapi",auth=(username, password) ,timeout=2, verify=False)
            
            if res.status_code == 200:
                is_connected_to_pi = True
            
        except requests.exceptions.RequestException:
            is_connected_to_pi = False


        excel = excel_repository.get_by_uuid(excel_id)

        if not excel:
            print(f"Excel {excel_id} not found")
            return response(404, False, "Excel not found")

        variables = variable_repository.get_by_multiple(
            attributes={"excel_id": excel_id, "in_out": type}
        )

        # variables_base_case = [
        #     {**variable_schema.dump(variable),
        #     "base_case": "N/A" if not variable.web_id else random.randint(7, 20)

        #     } for variable in variables
        # ]

        variables_base_case = [
            {**variable_schema.dump(variable),
             "base_case": variable.konstanta if variable.konstanta else
             (requests.get(f"https://10.47.0.54/piwebapi/streams/{variable.web_id}/value", auth=(username, password), verify=False).json().Value if (is_connected_to_pi and variable.web_id and variable.web_id != "Not used") else "N/A")}
            for variable in variables
        ]

        return response(
            200,
            True,
            "Variables retrieved successfully",
            variables_base_case,
        )

    @token_required
    @parse_params(
        Argument("is_bulk", location="args", required=False, type=int, default=0),
        Argument("excel_id", location="json", required=True, type=str),
        Argument("variables", location="json", required=False, type=list, default=None),
        Argument("input_name", location="json", required=False, type=str),
        Argument("short_name", location="json", required=False, type=str),
        Argument("excel_variable_name", location="json", required=False, type=str),
        Argument("satuan", location="json", required=False, type=str),
        Argument("in_out", location="json", required=False, type=str),
        Argument("category", location="json", required=False, type=str),
    )
    @Transactional(propagation=Propagation.REQUIRED)
    def post(
        self, user_id: str, is_bulk: int, excel_id: str, variables: list, **inputs
    ) -> Response:
        """Create a new variable"""
        if is_bulk:
            if not variables:
                return response(
                    400, False, "variables is required when 'is_bulk' is set"
                )
            variable_records = [
                Variable(created_by=user_id, excel_id=excel_id, **variable)
                for variable in variables
            ]
            variable_repository.create_bulk(variable_records)

        else:
            missing_input = next(
                (name for name, input in inputs.items() if not input), None
            )
            if missing_input:
                return response(
                    400,
                    False,
                    f"'{missing_input}' is required when 'is_bulk' is not set",
                )
            variable_repository.create(
                {"created_by": user_id}, "excel_id", excel_id, **inputs
            )

        return response(200, True, "Variable created successfully")


class VariableResource(Resource):

    @token_required
    def get(self, user_id: str, variable_id: str) -> Response:
        variable = variable_repository.get_by_uuid(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        return response(
            200, True, "Variable retrieved successfully", variable_schema.dump(variable)
        )

    @token_required
    def delete(self, user_id: str, variable_id: str) -> Response:
        """Delete a specific variable by id"""
        variable = variable_repository.get_by_uuid(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        variable_repository.delete(variable)

        return response(200, True, "Variable deleted successfully")

    @token_required
    @parse_params(
        Argument("category", location="json", required=False, type=str, default=None),
        Argument("short_name", location="json", required=False, type=str, default=None),
        Argument("input_name", location="json", required=False, type=str, default=None),
        Argument("satuan", location="json", required=False, type=str, default=None),
        Argument("is_pareto", location="json", required=False, type=int, default=None),
        Argument(
            "is_faktor_koreksi", location="json", required=False, type=str, default=None
        ),
        Argument(
            "is_nilai_losses", location="json", required=False, type=str, default=None
        ),
    )
    @Transactional(propagation=Propagation.REQUIRED)
    def put(self, user_id: str, variable_id: str, **inputs) -> Response:
        variable = variable_repository.get_by_uuid(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        variable_repository.update(variable, {"updated_by": user_id, **inputs})

        return response(200, True, "Variable updated successfully")


class VariableDataAddResource(Resource):
    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    def get(self, user_id: str) -> Response:

        data = fetch_data_from_api(f"http://localhost:8001/excels?type=all")
        excel = "5c220f24-b7e4-410a-b52e-8ffe25047fb6"

        variables_record = []

        variables = variable_repository.get_by_multiple({"excel_id": excel})

        variables_mapping = {
            variable.excel_variable_name: variable
            for variable in variables
        }

        for item in data['data']:
            # Check if data already in db

            variable = variables_mapping.get(item['excel_name'])

            if not variable:
                variables_record.append(Variable(
                    excel_id=excel,
                    category=item['category'],
                    input_name=item['short_name'],
                    excel_variable_name=item['excel_name'],
                    satuan=item['unit'],
                    is_pareto=True if (item['type'] == 'out' and item['short_name']) else False,
                    in_out=item['type'],
                    is_nphr=item['is_nphr'],
                    is_over_haul=item['is_overhaul'],
                    web_id=item['webId'],
                    created_by=user_id,
                    konsanta=item['constant']
                )
                )
            else:
                # Update dat
                variable.in_out = item['type']
                variable.is_pareto = True if (item['type'] == 'out' and item['short_name']) else False
                variable.is_nphr = item['is_nphr']
                variable.is_over_haul = item['is_overhaul']
                variable.web_id = item['webId']
                variable.updated_by = user_id
                variable.category = item['category']
                variable.input_name = item['short_name']
                variable.excel_variable_name = item['excel_name']
                variable.satuan = item['unit']
                variable.konstanta = item['constant']

        # Add new variables to db
        variable_repository.create_bulk(variables_record)

        return response(200, True, "Data add to DB")
