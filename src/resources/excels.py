from typing import List, Set
from uuid import UUID
from flask import Response
from flask_restful import Resource
from flask_restful.reqparse import Argument
from models.excels import Excels
from utils import parse_params, response
from repositories import ExcelsRepository
from utils.jwt_verif import token_required
from utils.util import fetch_data_from_api
from config import WINDOWS_EFFICIENCY_APP_API


class ExcelsResource(Resource):
    """Excels"""

    # @token_required
    def get(self) -> Response:
        """
        Get excels from source and create new ones if they don't exist.

        Args:
            user_id (UUID): The id of the user.

        Returns:
            Response: The response containing the excels.
        """
        existing_excel_names: Set[str] = {
            excel.excel_filename for excel in ExcelsRepository.get_by().all()
        }
        new_excel_names: Set[str] = (
            set(fetch_data_from_api(WINDOWS_EFFICIENCY_APP_API)["data"]["excels"])
            - existing_excel_names
        )
        [
            ExcelsRepository.create(name, "24d28102-4d6a-4628-9a70-665bcd50a0f0")
            for name in new_excel_names
        ]

        # Get all excels
        excels = [excel.excel_filename for excel in ExcelsRepository.get_by().all()]

        print(excels)

        return response(200, True, "Excels retrieved successfully", excels)


class ExcelResource(Resource):

    @token_required
    def get(self, user_id: str, excel_id: str) -> Response:
        """
        Get a specific excel by id

        Args:
            user_id (UUID): The id of the user.
            excel_id (str): The id of the excel to retrieve.

        Returns:
            Response: The response containing the excel.
        """
        excel = ExcelsRepository.get_by_id(excel_id)

        if not excel:
            return response(404, False, "Excel not found")

        return response(200, True, "Excel retrieved successfully", excel)

    def delete(self, user_id: str, excel_id: str) -> Response:
        """
        Delete a specific excel by id

        Args:
            user_id (UUID): The id of the user.
            excel_id (str): The id of the excel to delete.

        Returns:
            Response: The response containing the deleted excel.
        """
        excel = ExcelsRepository.get_by_id(excel_id)

        if not excel:
            return response(404, False, "Excel not found")

        ExcelsRepository.delete(excel_id)

        return response(200, True, "Excel deleted successfully")
