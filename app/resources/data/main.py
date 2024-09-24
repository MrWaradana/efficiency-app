from datetime import datetime

import requests
from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyTransaction)
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.controllers import data_controller
from app.repositories import DataRepository, VariablesRepository
from app.schemas.data import EfficiencyTransactionSchema
from core.cache.cache_manager import Cache
from core.config import config
from core.security.jwt_verif import token_required
from core.utils import get_key_by_value, parse_params, response

data_schema = EfficiencyTransactionSchema(exclude=["efficiency_transaction_details"])
data_schema_with_rel = EfficiencyTransactionSchema()
data_repository = DataRepository(EfficiencyTransaction)


class DataListResource(Resource):
    """
    Resource for retrieving and creating Transactions.
    """

    @token_required
    @parse_params(
        Argument("page", location="args", type=int, required=False, default=1),
        Argument("size", location="args", type=int, required=False, default=100),
        Argument("all", location="args", type=bool, required=False, default=False),
        Argument("start_date", location="args", type=str, required=False, default=None),
        Argument("end_date", location="args", type=str, required=False, default=None),
    )
    def get(self, user_id, page, size, all, start_date, end_date):
        # Apply pagination
        data = data_controller.paginated_list_data(
            page, size, all, start_date, end_date
        )
        return response(
            200,
            True,
            "Transactions retrieved successfully.",
            {
                **data[0],
                "transactions": [
                    {
                        **data_schema.dump(item),
                        "periode": f"{item.periode.strftime('%Y-%m-%d')} | {item.sequence}",
                    }
                    for item in data[1]
                ],
            },
        )

    @parse_params(
        Argument(
            "jenis_parameter",
            location="json",
            required=False,
            type=str,
            default="Current",
        ),
        Argument(
            "name",
            location="json",
            required=True,
            type=str,
        ),
        Argument("excel_id", location="json", required=True, type=str),
        Argument("inputs", location="json", required=True, type=dict),
        Argument("is_perfomance_test", location="json", required=False, type=bool, default=False),
    )
    @token_required
    def post(self, jenis_parameter, excel_id, inputs, user_id, name):
        data = data_controller.create_data(
            jenis_parameter, excel_id, inputs, user_id, name
        )

        return response(
            200,
            True,
            "Transaction created successfully",
            {"data_id": data},
        )


class DataResource(Resource):

    @token_required
    def get(self, transaction_id, user_id):
        if not transaction_id:
            return response(400, False, "Transaction ID is required")

        transaction = data_repository.get_by_uuid(transaction_id)
        # If the transaction is not found in the database, return a response with a 404 status code
        # and an error message.
        if not transaction:
            return response(404, False, "Data transaction not found")

        # If the transaction is found, return a response with a 200 status code and a success message,
        # along with the JSON representation of the transaction.
        return response(
            200,
            True,
            "Transaction retrieved successfully",
            data_schema_with_rel.dump(transaction),
        )

    @token_required
    def delete(self, user_id, transaction_id):
        data = data_controller.delete_data(transaction_id)

        return response(200, True, "Transaction deleted successfully", data_schema.dump(data))

    @token_required
    @parse_params(
        Argument("inputs", type=dict, required=True),
        Argument("name", type=str, required=False, default=None),
    )
    def put(self, transaction_id, user_id, inputs, name=None):
        data = data_controller.update_data(transaction_id, user_id, inputs, name)

        return response(200, True, "Transaction updated successfully", data_schema.dump(data))
