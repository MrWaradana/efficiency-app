from flask import Response
from flask_restful import Resource
from flask_restful.reqparse import Argument
from app.schemas import ExcelSchema
from app.controllers.excels import excel_controller
from core.security import token_required
from core.utils import parse_params, response

excel_schema = ExcelSchema()

class ExcelsResource(Resource):
    """Excels"""

    @token_required
    def get(self, user_id) -> Response:
        excels = excel_controller.get_all_excel()
        return response(
            200,
            True,
            "Excels retrieved successfully",
            excel_schema.dump(excels, many=True),
        )

    @parse_params(Argument("name", location="json", required=True))
    @token_required
    def post(self, user_id, name) -> Response:
        excel = excel_controller.create_excel(name, user_id)

        return response(
            201, True, "Excel created successfully", excel_schema.dump(excel)
        )


class ExcelResource(Resource):

    @token_required
    def get(self, excel_id: str, user_id: str) -> Response:
        excel = excel_controller.get_excel(excel_id=excel_id)
        if not excel:
            return response(404, False, "Excel not found")

        return response(
            200, True, "Excel retrieved successfully", excel_schema.dump(excel)
        )

    @token_required
    def delete(self, excel_id: str, user_id: str) -> Response:
        # Get the excel from the database by its id
        excel = excel_controller.get_excel(excel_id=excel_id)

        if not excel:
            return response(404, False, "Excel not found")

        excel_controller.delete_excel(excel)

        return response(200, True, "Excel deleted successfully")

    @token_required
    @parse_params(
        Argument("name", location="json", required=False, type=str, default=None)
    )
    def put(self, excel_id: str, user_id: str, name) -> Response:
        # Get the excel from the database by its id
        excel = excel_controller.get_excel(excel_id=excel_id)
        if not excel:
            return response(404, False, "Excel not found")
        excel_controller.update_excel(excel, name)
        return response(200, True, "Excel updated successfully")
