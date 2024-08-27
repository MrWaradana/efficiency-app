from datetime import datetime
from flask import request
from flask_restful import Resource
from flask_restful.reqparse import Argument
import requests
from config import config
from repositories.excels import ExcelsRepository
from utils import parse_params, response, get_key_by_value
from repositories import VariablesRepository, TransactionRepository
from sqlalchemy.exc import SQLAlchemyError
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import EfficiencyDataDetail

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

        # Parse start and end dates if provided
        start_date = datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        # Build the query based on the date range
        query = TransactionRepository.get_query(start_date=start_date, end_date=end_date)

        # Get the total count of records
        count = query.count()

        if all:
            # Retrieve all transactions without pagination
            transactions = query.all()
            transaction_data = [transaction.json for transaction in transactions]

            return response(200, True, "Data transactions retrieved successfully", {
                "transactions": transaction_data,
                "count": count
            })

        # Apply pagination
        paginated_query = query.paginate(page=page, per_page=size)
        transactions = [transaction.json for transaction in paginated_query.items]

        # Construct response
        return response(200, True, 'Transactions retrieved successfully.', {
            "current_page": paginated_query.page,
            "total_pages": paginated_query.pages,
            "page_size": paginated_query.per_page,
            "total_items": paginated_query.total,
            "has_next_page": paginated_query.has_next,
            "has_previous_page": paginated_query.has_prev,
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
        # Get variable mappings
        variables = VariablesRepository.get_by(excel_id=excel_id).all()
        variable_mappings = {str(var.id): {"name": var.input_name,
                                           "category": var.category} for var in variables}
        
        # Check if trasaction periode already exists
        # periode = datetime.strptime(periode, "%Y-%m-%d").date()
        
        is_periode_exist = TransactionRepository.get_by(periode=periode).first()
            
        if is_periode_exist:
            return response(400, False, "Data Transaction for this periode already exist", None)

        input_data = {}
        transaction_records = []

        transaction_parent = TransactionRepository.create(
            periode=periode,
            jenis_parameter=jenis_parameter,
            excel_id=excel_id,
            created_by=user_id
        )

        excel = ExcelsRepository.get_by(id=excel_id).first().excel_filename

        for key, value in inputs.items():
            variable_input = variable_mappings.get(key)

            if variable_input:
                variable_string = f"{variable_input['category']}: {variable_input['name']}" if variable_input["category"] else variable_input["name"]
                input_data[variable_string] = value

                transaction_records.append(EfficiencyDataDetail(
                    variable_id=key,
                    nilai=float(value),
                    nilai_string=None,
                    efficiency_transaction_id=transaction_parent.id,
                    created_by=user_id
                ))

        # Send data to API
        try:
            res = requests.post(f'{config.WINDOWS_EFFICIENCY_APP_API}/{excel}',
                                json={'inputs': input_data})
            res.raise_for_status()  # Raises an error for HTTP codes 4xx/5xx
        except requests.exceptions.RequestException as e:
            # Handle error, e.g., logging or retry mechanism
            print(f"API request failed: {e}")
            return response(500, False, "Failed to create transaction")

        outputs = res.json()

        for variable_title, input_value in outputs['data'].items():
            variable_id = get_key_by_value(variable_mappings, variable_title)
            value_float, value_string = None, None

            try:
                value_float = float(input_value)
            except ValueError:
                value_string = value

            if variable_id:
                transaction_records.append(EfficiencyDataDetail(
                    variable_id=variable_id,
                    efficiency_transaction_id=transaction_parent.id,
                    nilai=value_float,
                    nilai_string=value_string,
                    created_by=user_id
                ))

        try:
            db.session.add_all(transaction_records)

            transaction_parent.commit()
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            return response(500, False, str(e))

        return response(200, True, "Transaction created successfully")


class TransactionResource(Resource):

    def get(self, transaction_id):
        transaction = TransactionRepository.get_by_id(transaction_id)

        if not transaction:
            return response(404, False, "Data transaction not found")

        return response(200, True, "Transaction retrieved successfully", transaction.json)

    def delete(self, transaction_id):
        transaction = TransactionRepository.get_by_id(transaction_id)

        if not transaction:
            return response(404, False, "Transaction not found")

        TransactionRepository.delete(transaction_id)

        return response(200, True, "Transaction deleted successfully")

    @parse_params(
        Argument("inputs", location="json", required=True, type=dict),
    )
    @token_required
    def put(self, transaction_id, inputs, user_id):

        # Fetch the transaction and its details by ID
        transaction = TransactionRepository.get_by_id(transaction_id)

        if not transaction:
            return response(404, False, "Transaction not found")

         # Get variables mapping
        variables = VariablesRepository.get_by(excel_id=transaction.excel_id).all()
        variable_mappings = {var.id: {"name": var.input_name,
                                      "category": var.category} for var in variables}

        # Gather existing transaction details in bulk to minimize repeated queries
        existing_details = {detail.variable_id: detail for detail in transaction.efficiency_transaction_details.filter(
            EfficiencyTransactionDetail.variable_id.in_(inputs.keys())).all()}

        input_data = {}
        transaction_records = []

        for key, value in inputs.items():
            variable_input = variable_mappings.get(key)

            if variable_input:
                variable_string = f"{variable_input['category']}: {variable_input['name']}" if variable_input["category"] else variable_input["name"]
                input_data[variable_string] = value

                transaction_data = existing_details.get(key)

                if transaction_data:
                    transaction_data.nilai = value
                    transaction_data.updated_by = user_id
                    transaction_data.updated_at = datetime.now()
                else:
                    transaction_records.append(EfficiencyTransactionDetail(
                        variable_id=key,
                        nilai=value,
                        efficiency_transaction_id=transaction_id,
                        created_by=user_id
                    ))

        # Send data to API
        try:
            res = requests.post(f'{WINDOWS_EFFICIENCY_APP_API}/{transaction.excels.excel_filename}',
                                json={'inputs': input_data})
            res.raise_for_status()  # Raises an error for HTTP codes 4xx/5xx
        except requests.exceptions.RequestException as e:
            # Handle error, e.g., logging or retry mechanism
            print(f"API request failed: {e}")
            return response(500, False, str(e))

        outputs = res.json()
        for variable_title, input_value in outputs.items():
            variable_id = get_key_by_value(variable_mappings, variable_title)

            if variable_id:
                transaction_data = existing_details.get(variable_id)

                if transaction_data:
                    transaction_data.nilai = input_value
                    transaction_data.updated_by = user_id
                    transaction_data.updated_at = datetime.now()
                else:
                    transaction_records.append(EfficiencyTransactionDetail(
                        variable_id=variable_id,
                        efficiency_transaction_id=transaction_id,
                        nilai=input_value,
                        created_by=user_id
                    ))

        if transaction_records:
            db.session.bulk_save_objects(transaction_records)

        db.session.commit()
        return response(200, True, "Transaction updated successfully")
