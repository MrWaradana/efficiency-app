import random
from datetime import datetime
import time

import requests
from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyTransaction)


from app.repositories import DataRepository
from app.controllers.excels import excel_repository
from app.resources.variable.variable import variable_repository
from app.schemas.data import EfficiencyTransactionSchema
from app.schemas.variable import VariableSchema
from core.cache import Cache
from core.config import EnvironmentType, config
from core.controller import BaseController
from core.utils import get_key_by_value, response
from core.utils.formula import calculate_pareto
from core.factory import data_factory, variable_factory
from werkzeug import exceptions

data_repository = data_factory.data_repository
data_schema = data_factory.exclude_schema(["efficiency_transaction_details"])
variable_schema = variable_factory.variable_schema


class DataController(BaseController[EfficiencyTransaction]):
    def __init__(self, data_repository: DataRepository = data_repository):
        super().__init__(model=EfficiencyTransaction, repository=data_repository)
        self.data_repository = data_repository

    @Cache.cached(prefix="get_data_paginated")
    def paginated_list_data(self, page, size, all, start_date, end_date):
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
        query = self.data_repository.get_query(start_date=start_date, end_date=end_date, is_performance_test=False)

        # Get the total count of records
        count = data_repository._count(query)

        if all:
            # Retrieve all transactions without pagination
            transactions = data_repository._all(query)
            return {
                "current_page": None,
                "total_pages": None,
                "page_size": None,
                "has_next_page": None,
                "has_previous_page": None,
                "total_items": count,
            }, transactions

        # Apply pagination
        paginated_option, items = data_repository.paginate(query, page, size)

        return paginated_option, items

    @Cache.cached(prefix="get_performance_test_data_paginated")
    def paginated_performance_test_data(self, page, size, start_date, end_date):
        # Parse start and end dates if provided
        start_date = (
            datetime.strptime(start_date, "%Y-%m-%d").date() if start_date else None
        )
        end_date = datetime.strptime(end_date, "%Y-%m-%d").date() if end_date else None

        # Build the query based on the date range
        query = self.data_repository.get_query(start_date=start_date, end_date=end_date, is_performance_test=True)

        # Get the total count of records
        count = data_repository._count(query)

        # Apply pagination
        paginated_option, items = data_repository.paginate(query, page, size)

        return paginated_option, items

    @Transactional(propagation=Propagation.REQUIRED)
    def create_data(self, jenis_parameter, excel_id, inputs, user_id, name, is_performance_test, performance_test_weight):

        # Check connection to Excel Server
        try:
            res = requests.get(f"{config.WINDOWS_EFFICIENCY_APP_API}", timeout=5)
            res.raise_for_status()  # Raise an error if the API request fails
        except Exception as e:
            raise exceptions.InternalServerError("Failed to connect to Excel Server")

        excel = excel_repository.get_by_uuid(excel_id)

        if not excel:
            raise exceptions.NotFound("Excel not found")

        variables = variable_repository.get_by_excel_id(excel_id)

        variable_mappings = {
            str(var.id): {"name": var.input_name, "category": var.category}
            for var in variables
        }

        # Initialize empty dictionaries to store input data and transaction records
        input_data = {}
        transaction_records = []

        # Create Unique string for data transacntion identifier for execelAPI
        timestamp = int(time.time())
        unique_id = f"{name}_{timestamp}"

        # Create a new parent transaction
        transaction_parent = data_repository.create(
            {
                "name": name,
                "jenis_parameter": jenis_parameter,
                "excel_id": excel_id,
                "created_by": user_id,
                "sequence": data_repository.get_daily_increment(),
                "is_performance_test": is_performance_test,
                "performance_test_weight": performance_test_weight,
                "unique_id": unique_id,
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
        

        data_repository.create_bulk(transaction_records)
        
        
        # Send the input data to the Windows Efficiency API
        try:
            res = requests.post(
                f"{config.WINDOWS_EFFICIENCY_APP_API}/excels/{unique_id}",
                json={"inputs": input_data},
            )
        except requests.exceptions.RequestException as e:
            # Handle error, e.g., logging or retry mechanism
            print(f"API request failed: {e}")
            return response(500, False, "Failed to create transaction")

        # # Get the output data from the API response
        # outputs = res.json()

        # # Iterate over the output data
        # for variable_title, input_value in outputs["data"].items():
        #     variable_id = get_key_by_value(variable_mappings, variable_title)
        #     value_float, value_string = None, None
        #     try:
        #         if input_value is not None:
        #             value_float = float(input_value)
        #         # if config.ENVIRONMENT == EnvironmentType.DEVELOPMENT:
        #         #     value_float -= random.uniform(0.5, 7.5)

        #     except ValueError:
        #         value_string = value

        #     if variable_id:
        #         # Create a new transaction record with the output value and associated variable ID
        #         transaction_records.append(
        #             EfficiencyDataDetail(
        #                 variable_id=variable_id,
        #                 efficiency_transaction_id=transaction_parent.id,
        #                 nilai=value_float,
        #                 nilai_string=value_string,
        #                 created_by=user_id,
        #             )
        #         )

        # Bulk create the transaction records
        

        # Fetch data again for cahche
        Cache.remove_by_prefix("get_data_paginated")

        return transaction_parent.id

    def create_data_output(self, outputs, unique_id):
        # Get Data based on uniqueId
        transaction = data_repository.get_by_unique_id(unique_id)
        transaction_records = []

        excel = excel_repository.get_all()[0]

        if not excel:
            raise exceptions.NotFound("Excel not found")

        variables = variable_repository.get_by_excel_id(excel.id)

        variable_mappings = {
            str(var.id): {"name": var.input_name, "category": var.category}
            for var in variables
        }

        # Iterate over the output data
        for variable_title, input_value in outputs.items():
            variable_id = get_key_by_value(variable_mappings, variable_title)
            value_float, value_string = None, None
            try:
                if input_value is not None:
                    value_float = float(input_value)
                # if config.ENVIRONMENT == EnvironmentType.DEVELOPMENT:
                #     value_float -= random.uniform(0.5, 7.5)

            except ValueError:
                value_string = input_value

            if variable_id:
                # Create a new transaction record with the output value and associated variable ID
                transaction_records.append(
                    EfficiencyDataDetail(
                        variable_id=variable_id,
                        efficiency_transaction_id=transaction.id,
                        nilai=value_float,
                        nilai_string=value_string,
                        created_by=transaction.created_by,
                    )
                )
                
        # Bulk create the transaction records
        data_repository.create_bulk(transaction_records)
        
        return transaction.id

    @Transactional(propagation=Propagation.REQUIRED)
    def delete_data(self, transaction_id):

        data = data_repository.get_by_uuid(transaction_id)

        if not data:
            raise exceptions.NotFound("Data not found")

        data_repository.delete(data)
        Cache.remove_by_prefix("get_data_paginated")

        return data

    @Transactional(propagation=Propagation.REQUIRED)
    def update_data(self, transaction_id, user_id, inputs, name):
        transaction = data_repository.get_by_uuid(transaction_id)

        if not transaction:
            raise exceptions.NotFound("Data not found")

        if name:
            transaction.name = name

        variables = variable_repository.get_by_excel_id(transaction.excel_id)

        variable_mappings = {
            str(var.id): {"name": var.input_name, "category": var.category}
            for var in variables
        }

        existing_details = {
            detail.variable_id: detail
            for detail in transaction.efficiency_transaction_details
        }

        input_data = {}  # Initialize empty dictionary to store input data
        transaction_records = (
            []
        )  # Initialize empty list to store new transaction records

        for key, value in inputs.items():
            variable_input = variable_mappings.get(key)

            if variable_input:
                variable_string = (
                    f"{variable_input['category']}: {variable_input['name']}"
                    if variable_input["category"]
                    else variable_input["name"]
                )

                input_data[variable_string] = value

                existing_detail = existing_details.get(key)

                if existing_detail:
                    existing_detail.nilai = float(value)
                    existing_detail.nilai_string = None

                else:
                    transaction_records.append(
                        EfficiencyDataDetail(
                            variable_id=key,
                            nilai=float(value),
                            nilai_string=None,
                            efficiency_transaction_id=transaction.id,
                            created_by=user_id,
                        )
                    )

        try:
            res = requests.get(f"{config.WINDOWS_EFFICIENCY_APP_API}", timeout=5)
            res.raise_for_status()  # Raise an error if the API request fails

        except requests.exceptions.RequestException as e:
            raise exceptions.InternalServerError(str(e))

        outputs = res.json()

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
                existing_detail = existing_details.get(variable_id)

                if existing_detail:
                    existing_detail.nilai = value_float
                    existing_detail.nilai_string = value_string
                else:
                    transaction_records.append(
                        EfficiencyDataDetail(
                            variable_id=variable_id,
                            efficiency_transaction_id=transaction.id,
                            nilai=value_float,
                            nilai_string=value_string,
                            created_by=user_id,
                        )
                    )

        if transaction_records:
            data_repository.create_bulk(transaction_records)

        Cache.remove_by_prefix("get_data_paginated")

        return transaction

    def get_newest_data(self):
        return self.data_repository.get_newest_data()


data_controller = DataController()
