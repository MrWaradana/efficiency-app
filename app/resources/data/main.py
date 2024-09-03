import random
from datetime import datetime
from enum import Enum
from uuid import UUID

import requests
from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyTransaction)
from flask_restful import Resource
from flask_restful.reqparse import Argument
from sqlalchemy.orm import joinedload

from app.repositories import DataRepository, VariablesRepository
from app.repositories.excels import ExcelsRepository
from app.resources.excels import excel_repository
from app.resources.variable.main import variable_repository
from app.schemas.data import EfficiencyTransactionSchema
from core.config import EnvironmentType, config
from core.security.jwt_verif import token_required
from core.utils import get_key_by_value, now, parse_params, response
from core.utils.util import modify_number

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
        """
        Retrieve all Transactions.

        Args:
            user_id (int): The ID of the user making the request.
            page (int): The page number of the results.
            size (int): The number of results per page.
            all (bool): Flag indicating whether to retrieve all results without pagination.
            start_date (str): The start date of the query in the format "YYYY-MM-DD".
            end_date (str): The end date of the query in the format "YYYY-MM-DD".

        Returns:
            dict: Response containing the retrieved transactions and pagination information.
        """

        # Parse start and end dates if provided
        start_date = (
            datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        )
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        # Build the query based on the date range
        query = data_repository.get_query(start_date=start_date, end_date=end_date)

        # Get the total count of records
        count = data_repository._count(query)

        if all:
            # Retrieve all transactions without pagination
            transactions = data_repository._all(query)
            return response(
                200,
                True,
                "Data transactions retrieved successfully",
                {
                    "current_page": None,
                    "total_pages": None,
                    "page_size": None,
                    "has_next_page": None,
                    "has_previous_page": None,
                    "transactions": data_schema.dump(transactions, many=True),
                    "total_items": count,
                },
            )

        # Apply pagination
        paginated_option, items = data_repository.paginate(query, page, size)

        # Construct response
        return response(
            200,
            True,
            "Transactions retrieved successfully.",
            {
                **paginated_option,
                "transactions": data_schema.dump(items, many=True),
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
        Argument("excel_id", location="json", required=True, type=str),
        Argument("inputs", location="json", required=True, type=dict),
    )
    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    def post(self, jenis_parameter, excel_id, inputs, user_id):
        # Get variable mappings
        # Fetch all variables associated with the given excel_id
        excel = excel_repository.get_by_uuid(excel_id)

        if not excel:
            print(f"Excel {excel_id} not found")
            return response(404, False, "Excel not found")

        variables = variable_repository.get_by_excel_id(excel_id)

        # Create a dictionary of variable mappings where the keys are the variable IDs
        # and the values are dictionaries containing the variable name and category
        variable_mappings = {
            str(var.id): {"name": var.input_name, "category": var.category}
            for var in variables
        }

        # # Check if a transaction with the same periode already exists
        # is_periode_exist = data_repository.get_by_multiple(
        #     None, True, {"periode": periode, "jenis_parameter": "Current"}
        # )

        # if is_periode_exist:
        #     # If a transaction with the same periode already exists, return an error response
        #     return response(
        #         400, False, "Data Transaction for this periode already exist", None
        #     )

        # Initialize empty dictionaries to store input data and transaction records
        input_data = {}
        transaction_records = []

        # Create a new parent transaction
        transaction_parent = data_repository.create(
            {
                "jenis_parameter": jenis_parameter,
                "excel_id": excel_id,
                "created_by": user_id,
            }
        )

        # Get the filename of the Excel file associated with the transaction
        excel = excel_repository.get_by_uuid(excel_id).excel_filename

        # Iterate over the inputs dictionary
        for key, value in inputs.items():
            variable_input = variable_mappings.get(key)

            # If the variable ID exists in the variable mappings dictionary
            if variable_input:

                # Construct the variable string based on the category and name of the variable
                variable_string = (
                    f"{variable_input['category']}: {variable_input['name']}"
                    if variable_input["category"]
                    else variable_input["name"]
                )

                # Add the input value to the input_data dictionary with the variable string as the key
                input_data[variable_string] = value

                # Create a new transaction record with the input value and associated variable ID
                transaction_records.append(
                    EfficiencyDataDetail(
                        variable_id=key,
                        nilai=float(value),
                        nilai_string=None,
                        efficiency_transaction_id=transaction_parent.id,
                        created_by=user_id,
                    )
                )

        # Send the input data to the Windows Efficiency API
        try:
            res = requests.post(
                f"{config.WINDOWS_EFFICIENCY_APP_API}/{excel}",
                json={"inputs": input_data},
            )
            res.raise_for_status()  # Raise an error if the API request fails
        except requests.exceptions.RequestException as e:
            # Handle error, e.g., logging or retry mechanism
            print(f"API request failed: {e}")
            return response(500, False, "Failed to create transaction")

        # Get the output data from the API response
        outputs = res.json()

        # Iterate over the output data
        for variable_title, input_value in outputs["data"].items():
            variable_id = get_key_by_value(variable_mappings, variable_title)
            value_float, value_string = None, None

            try:
                value_float = float(input_value)
                if config.ENVIRONMENT == EnvironmentType.DEVELOPMENT:
                    value_float -= random.uniform(0.5, 7.5)

            except ValueError:
                value_string = value

            if variable_id:
                # Create a new transaction record with the output value and associated variable ID
                transaction_records.append(
                    EfficiencyDataDetail(
                        variable_id=variable_id,
                        efficiency_transaction_id=transaction_parent.id,
                        nilai=value_float,
                        nilai_string=value_string,
                        created_by=user_id,
                    )
                )

        # Bulk create the transaction records
        data_repository.create_bulk(transaction_records)

        # Return a success response
        return response(200, True, "Transaction created successfully")


class DataResource(Resource):

    @token_required
    def get(self, transaction_id, user_id):
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
    @Transactional(propagation=Propagation.REQUIRED)
    def delete(self, user_id, transaction_id):
        """
        This method handles the deletion of a transaction by its ID.

        Parameters:
            transaction_id (str): The ID of the transaction to be deleted.

        Returns:
            dict: A response dictionary containing a success flag, a success message, and a status code.
        """

        # Retrieve the transaction by its ID from the database
        # using the `TransactionRepository.get_by_id` method.
        transaction = data_repository.get_by_uuid(transaction_id)

        # If the transaction is not found in the database, return a response with
        # a 404 status code and an error message.
        if not transaction:
            return response(404, False, "Transaction not found")

        # If the transaction is found, delete it from the database
        # by calling the `delete` method of the transaction object.
        data_repository.delete(transaction)

        # After the transaction is deleted, return a response with a 200 status code,
        # a success message, and a success flag.
        return response(200, True, "Transaction deleted successfully")

    @token_required
    @Transactional(propagation=Propagation.REQUIRED)
    @parse_params(
        Argument("inputs", type=dict, required=True),
    )
    def put(self, transaction_id, user_id, inputs):
        """
        This method updates the transaction data with the specified ID.

        It fetches the transaction and its details by ID,
        retrieves the variables mapping, and gathers existing transaction details in bulk.
        It then iterates over the inputs and updates the transaction data accordingly.
        It sends the updated data to the Windows Efficiency App API and
        retrieves the outputs. It updates the transaction data and creates new transaction records if necessary.
        Finally, it returns a response indicating the success or failure of the transaction update.

        Parameters:
            transaction_id (str): The ID of the transaction to update.
            inputs (dict): A dictionary of input values for the transaction.
            user_id (int): The ID of the user making the request.

        Returns:
            dict: A response dictionary containing a success flag, a success message, and a status code.
        """
        # Fetch the transaction and its details by ID
        transaction = data_repository.get_by_uuid(transaction_id)

        return response(
            200,
            True,
            "Transaction retrieved successfully",
            data_schema.dump(transaction),
        )

        if not transaction:
            return response(404, False, "Transaction not found")

        # Create a dictionary of variable mappings where the keys are the variable IDs
        # and the values are dictionaries containing the variable name and category
        variables = VariablesRepository.get_by(excel_id=transaction.excel_id).all()
        variable_mappings = {
            str(var.id): {"name": var.input_name, "category": var.category}
            for var in variables
        }

        # Gather existing transaction details in bulk to minimize repeated queries
        # Fetch all existing data details for the transaction
        existing_details = {
            detail.variable_id: detail
            for detail in transaction.efficiency_transaction_details
        }

        raise Exception(existing_details)

        input_data = {}  # Initialize empty dictionary to store input data
        transaction_records = (
            []
        )  # Initialize empty list to store new transaction records

        # Iterate over the inputs and update the transaction data accordingly
        for key, value in inputs.items():
            variable_input = variable_mappings.get(
                key
            )  # Get variable mapping for the input variable

            if variable_input:
                variable_string = (
                    f"{variable_input['category']}: {variable_input['name']}"
                    if variable_input["category"]
                    else variable_input["name"]
                )
                input_data[variable_string] = value  # Store input data in a dictionary

                transaction_data = existing_details.get(
                    key
                )  # Get existing data detail for the variable

                if transaction_data:
                    transaction_data.nilai = (
                        value  # Update value of existing data detail
                    )
                    transaction_data.updated_by = (
                        user_id  # Update updated_by of existing data detail
                    )
                    transaction_data.updated_at = datetime.now(
                        config.TIMEZONE
                    )  # Update updated_at of existing data detail
                else:
                    transaction_records.append(
                        EfficiencyDataDetail(  # Create new data detail
                            variable_id=key,
                            nilai=value,
                            nilai_string=None,
                            efficiency_transaction_id=transaction_id,
                            created_by=user_id,
                        )
                    )

        # Send data to API
        try:
            # Send input data to the Windows Efficiency App API and retrieve outputs
            res = requests.post(
                f"{config.WINDOWS_EFFICIENCY_APP_API}/{transaction.excels.excel_filename}",
                json={"inputs": input_data},
            )
            res.raise_for_status()  # Raise an error for HTTP codes 4xx/5xx
        except requests.exceptions.RequestException as e:
            # Handle error, e.g., logging or retry mechanism
            print(f"API request failed: {e}")
            return response(500, False, str(e))

        outputs = res.json()  # Parse response as JSON

        # Iterate over the outputs and update the transaction data accordingly
        for variable_title, input_value in outputs.items():
            variable_id = get_key_by_value(
                variable_mappings, variable_title
            )  # Get variable ID from variable mapping

            if variable_id:
                transaction_data = existing_details.get(
                    variable_id
                )  # Get existing data detail for the variable

                if transaction_data:
                    transaction_data.nilai = (
                        input_value  # Update value of existing data detail
                    )
                    transaction_data.updated_by = (
                        user_id  # Update updated_by of existing data detail
                    )
                    transaction_data.updated_at = datetime.now(
                        config.TIMEZONE
                    )  # Update updated_at of existing data detail
                else:
                    transaction_records.append(
                        EfficiencyDataDetail(  # Create new data detail
                            variable_id=variable_id,
                            efficiency_transaction_id=transaction_id,
                            nilai=input_value,
                            nilai_string=None,
                            created_by=user_id,
                        )
                    )

        if transaction_records:  # If there are new transaction records
            TransactionRepository.bulk_create(
                transaction_records
            )  # Create new data details in the database

        return response(200, True, "Transaction updated successfully")
