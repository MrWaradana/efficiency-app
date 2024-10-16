from digital_twin_migration.models.pfi_app import PFICategory, PFIEquipment
from datetime import datetime

import requests
from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail,
    EfficiencyTransaction,
    ThermoflowStatus
)
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.controllers import data_controller
from app.repositories import DataRepository, VariablesRepository
from app.schemas.data import EfficiencyTransactionSchema
from core.cache import redis, RedisBackend, cache_flask
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
        Argument(
            "is_performance_test",
            location="args",
            type=int,
            required=False,
            default=0,
        ),
    )
    def get(self, user_id, page, size, all, start_date, end_date, is_performance_test):
        # Get Thermoflow status
        # status = ThermoflowStatus.query.first().is_running

        # Apply pagination
        data = (
            data_controller.paginated_list_data(page, size, all, start_date, end_date)
            if not is_performance_test
            else data_controller.paginated_performance_test_data(
                page, size, start_date, end_date
            )
        )
        
        selected_data = redis.get("selected_data")

        return response(
            200,
            True,
            "Transactions retrieved successfully.",
            {
                "thermo_status": False,
                ** data[0],
                "transactions": [
                    {
                        **data_schema.dump(item),
                        "status": redis.hget(f'process:{item.unique_id}', 'status').decode('utf-8') if redis.hget(f'process:{item.unique_id}', 'status') else item.status,
                        "periode": f"{item.periode.strftime('%Y-%m-%d')} | {item.sequence}",
                        "is_selected": str(item.id) == selected_data
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
            default="current",
        ),
        Argument(
            "name",
            location="json",
            required=True,
            type=str,
        ),
        Argument("excel_id", location="json", required=True, type=str),
        Argument("inputs", location="json", required=True, type=dict),
        Argument(
            "is_performance_test",
            location="json",
            required=False,
            type=bool,
            default=False,
        ),
        Argument(
            "performance_test_weight",
            location="json",
            required=False,
            type=int,
            default=100,
        ),
    )
    @token_required
    def post(
        self,
        jenis_parameter,
        excel_id,
        inputs,
        user_id,
        name,
        is_performance_test,
        performance_test_weight,
    ):
        data = data_controller.create_data(
            jenis_parameter,
            excel_id,
            inputs,
            user_id,
            name,
            is_performance_test,
            performance_test_weight,
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
            data_schema.dump(transaction),
        )
    
    def post(self, transaction_id, user_id):
        if not transaction_id:
            return response(400, False, "Transaction ID is required")
        
        transaction = data_repository.get_by_uuid(transaction_id)
        # If the transaction is not found in the database, return a response with a 404 status code
        # and an error message.
        if not transaction:
            return response(404, False, "Data transaction not found")
        
        # Save selected transaction id to redis
        
        redis.set("selected_data", transaction_id)
        
        return response(
            200,
            True, 
            "Selected Transaction saved successfully"
        )

    @token_required
    def delete(self, user_id, transaction_id):
        data = data_controller.delete_data(transaction_id)

        return response(
            200, True, "Transaction deleted successfully", data_schema.dump(data)
        )

    @token_required
    @parse_params(
        Argument("inputs", type=dict, required=True),
        Argument("name", type=str, required=False, default=None),
    )
    def put(self, transaction_id, user_id, inputs, name=None):
        data = data_controller.update_data(transaction_id, user_id, inputs, name)

        return response(
            200, True, "Transaction updated successfully", data_schema.dump(data)
        )


class DataOutputResource(Resource):
    @parse_params(
        Argument("outputs", type=dict, required=True),
        Argument("unique_id", type=str, required=True),
    )
    def post(self, outputs, unique_id):
        data = data_controller.create_data_output(outputs, unique_id)
        return response(200, True, "Data retrieved successfully")


class DataPerformanceResource(Resource):

    def get(self):
        data = data_controller.get_performance_test_chart_data()

        return response(200, True, "Data retrieved successfully", data)


class DataStatusThermoflow(Resource):

    def get(self):
        # status = ThermoflowStatus.query.first().is_running

        return response(200, True, "Data retrieved successfully", {"thermo_status": False})