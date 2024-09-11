import random

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import (Variable,
                                                          VariableCause)
from flask import Response, request
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.repositories import VariablesRepository
from app.resources.excels import excel_repository
from app.schemas import (VariableCauseSchema, VariableHeaderSchema,
                         VariableSchema)
from core.config import config
from core.security.jwt_verif import token_required
from core.utils import parse_params, response
from core.utils.util import fetch_data_from_api

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
        excel = excel_repository.get_by_uuid(excel_id)

        if not excel:
            print(f"Excel {excel_id} not found")
            return response(404, False, "Excel not found")

        variables = variable_repository.get_by_multiple(
            attributes={"excel_id": excel_id, "is_pareto": True, "in_out": type}
        )

        variables_base_case = [
            {**variable_schema.dump(variable), "base_case": random.randint(7, 20)}
            for variable in variables
        ]

        return response(
            200,
            True,
            "Variables retrieved successfully",
            variables_base_case,
        )

        # existing_variables = {
        #     var.excel_variable_name
        #     for var in VariablesRepository.get_by(excel_id=excel_id).all()
        # }

        # source_variables = fetch_data_from_api(
        #     f"{config.WINDOWS_EFFICIENCY_APP_API}/{excel.excel_filename}"
        # )

        # if not source_variables:
        #     print(f"Failed to get variables from {excel.excel_filename}")
        #     return response(404, False, "Get VARIABLES failed")

        # variable_records = []

        # for variable in source_variables["data"]:
        #     if f"{variable['category']}: {variable['variabel']}" in existing_variables:
        #         continue
        #     else:
        #         new_var = Variable(
        #             excel_id=excel_id,
        #             input_name=variable["variabel"],
        #             satuan=variable["unit"],
        #             in_out=variable["type"],
        #             excel_variable_name=f"{variable['category']}: {variable['variabel']}",
        #             created_by="24d28102-4d6a-4628-9a70-665bcd50a0f0",
        #             category=variable["category"],
        #             short_name=variable["variabel"],
        #         )
        #         new_var.is_pareto = True
        #         variable_records.append(new_var)

        # db.session.add_all(variable_records)
        # db.session.commit()

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
