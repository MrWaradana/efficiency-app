from typing import Set

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import Excel
from flask import Response
from flask_restful import Resource
from flask_restful.reqparse import Argument
from sqlalchemy.orm import joinedload

from app.repositories import ExcelsRepository
from app.schemas import ExcelSchema
from core.security import token_required
from core.utils import parse_params, response
from core.utils.util import fetch_data_from_api

excel_schema = ExcelSchema()
excel_repository = ExcelsRepository(Excel)


class ExcelsResource(Resource):
    """Excels"""

    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    def get(self, user_id) -> Response:
        # # Fetch all existing excel filenames from the database
        # existing_excel_names: Set[str] = {
        #     excel.excel_filename for excel in ExcelsRepository.get_by().all()
        # }

        # # Fetch all excel filenames from the source API and remove the ones that already exist
        # source_excel_data = fetch_data_from_api(config.WINDOWS_EFFICIENCY_APP_API)
        # source_excel_names = set(source_excel_data["data"]["excels"])
        # new_excel_names = source_excel_names - existing_excel_names

        # # Create new excel objects for the new excels in the database
        # [
        #     ExcelsRepository.create(excel_filename=name, created_by=user_id)
        #     for name in new_excel_names
        # ]

        # Fetch all excel objects from the database
        excels = excel_repository.get_all()

        # Return a response containing all excels
        return response(
            200,
            True,
            "Excels retrieved successfully",
            excel_schema.dump(excels, many=True),
        )

    @parse_params(Argument("name", location="json", required=True))
    @token_required
    def post(self, user_id, name) -> Response:
        excel = excel_repository.create({"excel_filename": name, "created_by": user_id})

        return response(
            201, True, "Excel created successfully", excel_schema.dump(excel)
        )


class ExcelResource(Resource):

    @token_required
    def get(self, excel_id: str, user_id: str) -> Response:
        # Get the excel from the database by its id
        excel = excel_repository.get_by_uuid(excel_id)

        # If the excel is not found, return a response indicating that the excel was not found
        if not excel:
            return response(404, False, "Excel not found")

        # Return a response containing the excel
        return response(
            200, True, "Excel retrieved successfully", excel_schema.dump(excel)
        )

    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    def delete(self, excel_id: str, user_id: str) -> Response:
        # Get the excel from the database by its id
        excel = excel_repository.get_by_uuid(excel_id)

        # If the excel is not found, return a response indicating that the excel was not found
        if not excel:
            return response(404, False, "Excel not found")

        # Delete the excel from the database
        excel_repository.delete(excel)

        # Return a response indicating that the excel was deleted successfully
        return response(200, True, "Excel deleted successfully")

    @token_required
    @parse_params(
        Argument("name", location="json", required=False, type=str, default=None)
    )
    @Transactional(propagation=Propagation.REQUIRED)
    def put(self, excel_id: str, user_id: str, name) -> Response:
        # Get the excel from the database by its id
        excel = excel_repository.get_by_uuid(excel_id)

        # If the excel is not found, return a response indicating that the excel was not found
        if not excel:
            return response(404, False, "Excel not found")

        # Update the excel in the database
        excel_repository.update(excel, {"excel_filename": name})

        # Return a response indicating that the excel was updated successfully
        return response(200, True, "Excel updated successfully")
