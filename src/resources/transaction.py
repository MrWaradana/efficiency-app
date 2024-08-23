from datetime import datetime
from flask import request
from flask_restful import Resource
from flask_restful.reqparse import Argument
import requests
from config import WINDOWS_EFFICIENCY_APP_API
from utils import parse_params, response, get_key_by_value
from repositories import VariablesRepository, TransactionRepository
from sqlalchemy.exc import SQLAlchemyError
from digital_twin_migration.models import db, EfficiencyTransactionDetail

from utils.jwt_verif import token_required


class TransactionsResource(Resource):
    """CaseInputs"""

    @token_required
    @parse_params(
        Argument("page", location="args", type=int, required=False, default=1),
        Argument("size", location="args", type=int, required=False, default=100),
        Argument("all", location="args", type=bool, required=False, default=False),
        Argument("start_date", location="args", type=str, required=False, default=None),
        Argument("end_date", location="args", type=str, required=False, default=None),
    )
    def get(self, user_id, page, size, all, start_date, end_date):
        """Retrieve all Transactions"""
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        query = TransactionRepository.get_query(start_date=start_date, end_date=end_date)
        count = query.count()

        if all:
            query = query.all()

            return response(200, True, "Transactions retrieved successfully", {"transactions": [transaction.json for transaction in query], "count": count})

        query = query.paginate(page=page, per_page=size)
        transactions = [transaction.json for transaction in query]

        return response(200, True, 'Transactions retrieved successfully.',
                        {"current_page": query.page,
                         "total_pages": query.pages,
                         "page_size": query.per_page,
                         "total_items": query.total,
                         "has_next_page": query.has_next,
                         "has_previous_page": query.has_prev,
                         "transactions": transactions,
                         })

    @parse_params(Argument("periode", location="json", required=True, type=str),
                  Argument("jenis_parameter", location="json", required=True, type=str),
                  Argument("excel_id", location="json", required=True, type=str),
                  Argument("inputs", location="json", required=True, type=dict),
                  )
    @token_required
    def post(self, periode, jenis_parameter, excel_id, inputs, user_id):
        """Create a new Transaction"""
        variable_mappings = {var.id: {"name": var.input_name, "category": var.category}
                             for var in VariablesRepository.get_by(excel_id=excel_id).all()}
        input_data = {}
        transaction_records = []

        transaction_parent = TransactionRepository.create(
            periode=periode,
            jenis_parameter=jenis_parameter,
            excel_id=excel_id,
            created_by=user_id
        )

        for key, value in inputs.items():
            variable_input = variable_mappings.get(key)
            variable_string = f"{variable_input['category']}: {variable_input['name']}" if variable_input["category"] else variable_input["name"]
            input_data[variable_string] = value

            transaction_records.append(EfficiencyTransactionDetail(
                variable_id=key,
                nilai=value,
                efficiency_transaction_id=transaction_parent.id,
                created_by=user_id
            ))

        # TransactionRepository.bulk_create(transaction_records)

        # Send data to API
        try:
            res = requests.post(WINDOWS_EFFICIENCY_APP_API, json=input_data)
            res.raise_for_status()  # Raises an error for HTTP codes 4xx/5xx
        except requests.exceptions.RequestException as e:
            # Handle error, e.g., logging or retry mechanism
            print(f"API request failed: {e}")
            return response(500, False, "Failed to create transaction")

        outputs = res.json()

        for variable_title, input_value in outputs.items():
            variable_id = get_key_by_value(variable_mappings, variable_title)

            transaction_records.append(EfficiencyTransactionDetail(
                variable_id=variable_id,
                efficiency_transaction_id=transaction_parent.id,
                nilai=input_value,
                created_by=user_id
            ))

        try:
            transaction_parent.commit()

            db.session.bulk_save_objects(transaction_records)
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return response(500, False, "Failed to create transaction")

        return response(200, True, "Transaction created successfully")


class TransactionResource(Resource):

    def get(self, transaction_id):
        transaction = TransactionRepository.get_by_id(transaction_id)

        if not transaction:
            return response(404, False, "Transaction not found")

        return response(200, True, "Transaction retrieved successfully", transaction.json)

    def delete(self, transaction_id):
        transaction = TransactionRepository.get_by_id(transaction_id)

        if not transaction:
            return response(404, False, "Transaction not found")

        TransactionRepository.delete(transaction_id)

        return response(200, True, "Transaction deleted successfully")

    @parse_params(
        Argument("periode", location="json", type=str, default=None),
        Argument("jenis_parameter", location="json", type=str, default=None),
    )
    def put(self, transaction_id, periode, jenis_parameter):

        transaction = TransactionRepository.get_by_id(transaction_id)

        if not transaction:
            return response(404, False, "Transaction not found")

        TransactionRepository.update(transaction_id, periode=periode,
                                     jenis_parameter=jenis_parameter)

        return response(200, True, "Transaction updated successfully")
