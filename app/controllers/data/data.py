import random
from datetime import datetime

import requests
from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyTransaction)

from app.repositories import DataRepository
from app.resources.excels import excel_repository
from app.resources.variable.main import variable_repository
from app.schemas.data import EfficiencyTransactionSchema
from app.schemas.variable import VariableSchema
from core.cache import Cache
from core.config import EnvironmentType, config
from core.controller import BaseController
from core.utils import get_key_by_value, response
from core.utils.formula import calculate_pareto

data_repository = DataRepository(EfficiencyTransaction)
data_schema = EfficiencyTransactionSchema(exclude=["efficiency_transaction_details"])
variable_schema = VariableSchema()


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
        query = self.data_repository.get_query(start_date=start_date, end_date=end_date)

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

    @Transactional(propagation=Propagation.REQUIRED)
    def create_data(self, jenis_parameter, excel_id, inputs, user_id, name):

        # Check connection to Excel Server
        try:
            res = requests.get(f"{config.WINDOWS_EFFICIENCY_APP_API}", timeout=5)
            res.raise_for_status()  # Raise an error if the API request fails
        except requests.exceptions.RequestException as e:
            # Handle error, e.g., logging or retry mechanism
            print(f"API request failed: {e}")
            return response(500, False, "Connection to Excel Server failed")

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
                "name": name,
                "jenis_parameter": jenis_parameter,
                "excel_id": excel_id,
                "created_by": user_id,
                "sequence": data_repository.get_daily_increment(),
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

        # Fetch data again for cahche
        Cache.remove_by_prefix("get_data_paginated")

        return transaction_parent.id

    def get_data_trending(self, start_date: str, end_date: str, variable_ids: str):
        """
        This function retrieves trending data for specified variable IDs within a specified date range.

        :param start_date: The `start_date` parameter is a string that represents the beginning date of
        the time period for which you want to retrieve trending data. This date is typically in a
        specific format, such as "YYYY-MM-DD", to indicate the year, month, and day
        :type start_date: str
        :param end_date: The `end_date` parameter is a string that represents the end date for the data
        you want to retrieve. It is used to specify the date up to which you want to fetch the data
        :type end_date: str
        :param variable_ids: A list of variable IDs that you want to retrieve data for. These IDs could
        represent different metrics or data points that you are interested in analyzing
        :type variable_ids: str
        """

        # check if variable id contains (,)
        if ',' in variable_ids:
            variable_ids_list = variable_ids.split(',')
        else:
            variable_ids_list = [variable_ids]

        data = data_repository.get_data_trending(start_date, end_date, variable_ids_list)
        data_target = data_repository.get_target_data_by_variable(variable_ids_list)

        result = []

        for item in data:
            pareto = []
            current_data_details = item.efficiency_transaction_details
            target_data_details = data_target.efficiency_transaction_details

            target_mapping = {
                efficiency_transaction_detail.variable_id : efficiency_transaction_detail
                for efficiency_transaction_detail in target_data_details
            }

            for current_detail in current_data_details:
                target_detail = target_mapping.get(current_detail.variable_id)

                gap, persen_losses, nilai_losses = calculate_pareto(
                    target_detail, current_detail
                )

                pareto.append({
                    "id": current_detail.id,
                    "variable_name": current_detail.variable.input_name,
                    "variable_category": current_detail.variable.category,
                    "existing_data": current_detail.nilai,
                    "reference_data": target_detail.nilai,
                    "persen_losses": persen_losses,
                    "nilai_losses": nilai_losses,
                    "gap": gap,

                })

            result.append({**data_schema.dump(item), "pareto": pareto})

        return result


data_controller = DataController()
