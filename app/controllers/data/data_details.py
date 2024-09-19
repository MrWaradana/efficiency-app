from collections import defaultdict

from digital_twin_migration.database import Propagation, Transactional, db
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyTransaction)
from flask_restful import Resource
from flask_restful.reqparse import Argument

from app.controllers.data.data import data_repository
from app.repositories.data_detail import DataDetailRepository
from app.schemas import EfficiencyDataDetailSchema, VariableSchema
from core.cache import Cache
from core.controller.base import BaseController
from core.security import token_required
from core.utils import (calculate_gap, calculate_pareto,
                        calculate_persen_losses, parse_params, response)
from core.factory import data_detail_factory, variable_factory
from werkzeug import exceptions as exc

variable_schema = variable_factory.variable_schema
data_details_schema = data_detail_factory.data_detail_schema
data_detail_repository = data_detail_factory.data_detail_repository


class DataDetailController(BaseController[EfficiencyDataDetail]):
    def __init__(
        self, data_detail_repository: DataDetailRepository = data_detail_repository
    ):
        super().__init__(model=EfficiencyTransaction, repository=data_detail_repository)
        self.data_detail_repository = data_detail_repository

    def get_data_details(self, transaction_id: str, type: str):
        @Cache.cached(f"data_details_{transaction_id}_{type}")
        def fetch_data_details():
            data_details = self.data_detail_repository.get_by_data_id_and_variable_type(
                transaction_id, type
            )

            return data_details

        return fetch_data_details()

    def get_data_detail(self, detail_id: str):
        @Cache.cached(f"data_detail_{detail_id}")
        def fetch_data_detail():
            data_detail = self.data_detail_repository.get_by_uuid(detail_id)

            if not data_detail:
                return exc.NotFound("Data detail not found")

            return data_detail

        return fetch_data_detail()


data_detail_controller = DataDetailController()
