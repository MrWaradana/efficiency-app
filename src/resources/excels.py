from typing import List, Set
from uuid import UUID
from flask import Response
from flask_restful import Resource
from flask_restful.reqparse import Argument
from utils import parse_params, response
from repositories import ExcelsRepository
from utils.jwt_verif import token_required
from utils.util import fetch_data_from_api
from config import config

from digital_twin_migration.database import Transactional, Propagation

class ExcelsResource(Resource):
    """Excels"""

    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    def get(self, user_id) -> Response:
        """
        Fetches all existing excels from the database and creates new excels if
        they don't exist. Then, returns a response containing all excels.

        Args:
            user_id (UUID): The id of the user.

        Returns:
            Response: The response containing the excels.
        """

        # Fetch all existing excel filenames from the database
        existing_excel_names: Set[str] = {
            excel.excel_filename
            for excel in ExcelsRepository.get_by().all()
        }

        # Fetch all excel filenames from the source API and remove the ones that already exist
        source_excel_data = fetch_data_from_api(config.WINDOWS_EFFICIENCY_APP_API)
        source_excel_names = set(source_excel_data["data"]["excels"])
        new_excel_names = source_excel_names - existing_excel_names

        # Create new excel objects for the new excels in the database
        [
            ExcelsRepository.create(name, user_id)
            for name in new_excel_names
        ]

        # Fetch all excel objects from the database
        excels = [excel.json for excel in ExcelsRepository.get_by().all()]

        # Return a response containing all excels
        return response(
            200,
            True,
            "Excels retrieved successfully",
            excels
        )


class ExcelResource(Resource):

    @token_required
    def get(self, excel_id: str, user_id: str) -> Response:
        """
        Get a specific excel by id

        Args:
            excel_id (str): The id of the excel to retrieve.
            user_id (UUID): The id of the user.

        Returns:
            Response: The response containing the excel.

        This function gets a specific excel by its id from the database.
        If the excel is found, it returns a response containing the excel.
        If the excel is not found, it returns a response indicating that the excel was not found.
        """
        # Get the excel from the database by its id
        excel = ExcelsRepository.get_by_id(excel_id)

        # If the excel is not found, return a response indicating that the excel was not found
        if not excel:
            return response(404, False, "Excel not found")

        # Return a response containing the excel
        return response(200, True, "Excel retrieved successfully", excel.json)

    @token_required
    def delete(self, excel_id: str, user_id: str) -> Response:
        """
        Delete a specific excel by id

        Args:
            excel_id (str): The id of the excel to delete.
            user_id (UUID): The id of the user.

        Returns:
            Response: The response containing the deleted excel.

        This function deletes a specific excel by its id from the database.
        If the excel is found and deleted, it returns a response indicating that the excel was deleted successfully.
        If the excel is not found, it returns a response indicating that the excel was not found.
        """
        # Get the excel from the database by its id
        excel = ExcelsRepository.get_by_id(excel_id)

        # If the excel is not found, return a response indicating that the excel was not found
        if not excel:
            return response(404, False, "Excel not found")

        # Delete the excel from the database
        ExcelsRepository.delete(excel_id)

        # Return a response indicating that the excel was deleted successfully
        return response(200, True, "Excel deleted successfully")
