
import random
from datetime import datetime

import requests
from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail,
    EfficiencyTransaction,
)


from app.repositories import DataRepository, VariablesRepository
from app.resources.excels import excel_repository
from app.resources.variable.main import variable_repository
from app.schemas.data import EfficiencyTransactionSchema
from core.config import EnvironmentType, config
from core.security.jwt_verif import token_required
from core.utils import get_key_by_value, parse_params, response
from core.controller import BaseController
from core.cache import Cache
data_repository = DataRepository(EfficiencyTransaction)


class DataController(BaseController[EfficiencyTransaction]):
    def __init__(self, data_repository: DataRepository = data_repository):
        super().__init__(model=EfficiencyTransaction, repository=data_repository)
        self.data_repository = data_repository

    
    # @Cache.cached(prefix="get_data_paginated")
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
            return transactions, count

        # Apply pagination
        paginated_option, items = data_repository.paginate(query, page, size)

        return paginated_option, items


data_controller = DataController()
