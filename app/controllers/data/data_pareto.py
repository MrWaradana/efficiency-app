from collections import defaultdict
from functools import partial
from multiprocessing import cpu_count, Pool

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
                        calculate_persen_losses, parse_params, response, calculate_cost_benefit, process_single_data_pareto)
from core.factory import data_detail_factory, variable_factory
from werkzeug import exceptions
variable_schema = variable_factory.variable_schema
data_details_schema = data_detail_factory.data_detail_schema
data_detail_repository = data_detail_factory.data_detail_repository


class DataParetoController(BaseController[EfficiencyDataDetail]):
    def __init__(
        self, data_detail_repository: DataDetailRepository = data_detail_repository
    ):
        super().__init__(model=EfficiencyTransaction, repository=data_detail_repository)
        self.data_detail_repository = data_detail_repository

    def get_newest_transaction_id(self):
        transaction = data_repository.get_newest_transaction()
        return transaction.id

    @Transactional(propagation=Propagation.REQUIRED)
    def get_data_pareto(self, transaction_id, percent_threshold=None):
        result_pareto = []
        total_persen = 0
        total_biaya = 0
        total_cost_benefit = 0

        is_cost_benefit = percent_threshold is None

        transaction_data = data_repository.get_by_uuid(transaction_id)
        if not transaction_data:
            raise exceptions.NotFound("Transaction not found")

        categorized_data = data_detail_repository.get_data_pareto(transaction_id)
        uncategorized_data = data_detail_repository.get_data_pareto(transaction_id, is_uncategorized=True)
        nphr = data_detail_repository.get_data_nphr(transaction_id).nilai
    

        if categorized_data is None or uncategorized_data is None:
            raise exceptions.NotFound("Data not found")
    
        
        # # Process data in parallel
        # with Pool(processes=cpu_count() - 1 or 1) as pool:
        #     processed_categirized_data = pool.map(process_func, categorized_data)
        #     processed_uncategorized_data = pool.map(process_func, uncategorized_data)

        calculated_data_by_category = defaultdict(list)
        calculated_data_uncategorized = defaultdict(list)
        aggregated_value = defaultdict(lambda: {
            'persen_losses': 0,
            'total_biaya': 0,
            'cost_benefit': 0
        })
        
        for item in categorized_data:
            payload = process_single_data_pareto(nphr, variable_schema, item)
            category = item['category']
            aggregated_value[category]['persen_losses'] += item['persen_losses'] or 0
            aggregated_value[category]['total_biaya'] += item['total_biaya'] or 0
            aggregated_value[category]['cost_benefit'] += item['cost_benefit'] or 0
            calculated_data_by_category[category].append(item)

        for item in uncategorized_data:
            payload = process_single_data_pareto(nphr, variable_schema, item)
            calculated_data_uncategorized.append(item)

        # Sort aggregated losses only once, limit looping
        sorted_aggregated_value = dict(
            sorted(aggregated_value.items(), key=lambda x: x[1]['persen_losses'], reverse=True)
        )

        result_chart = [{"category": category, "total_persen_losses": value['persen_losses'], "total_nilai_losses": (value['persen_losses'] / 100) * 1000} for category, value in sorted_aggregated_value.items()]

        for category, value in sorted_aggregated_value.items():
            total_persen += value['persen_losses']
            if percent_threshold and total_persen >= percent_threshold:
                total_persen -= value['persen_losses']
                break

            total_biaya += value['total_biaya']
            total_cost_benefit += value['cost_benefit']

            sorted_calculated_data = sorted(
                calculated_data_by_category[category],
                key=lambda x: x["persen_losses"],
                reverse=True,
            )

            payload = {
                "category": category,
                "total_persen_losses": value['persen_losses'],
                "total_nilai_losses": (value['persen_losses'] / 100) * 1000,
                "total_cost_gap": value['total_biaya'],
                "total_cost_benefit": value['cost_benefit'],
                "data": sorted_calculated_data,
            } if not is_cost_benefit else {
                "category": category,
                "total_cost_benefit": value['cost_benefit'],
            }

            result_pareto.append(payload)
    

        # update persen_threshold
        if not is_cost_benefit:
            transaction_data.persen_threshold = percent_threshold

        total_losses = (total_persen / 100) * 1000

        return result_pareto, result_chart, total_persen, total_losses, total_biaya, total_cost_benefit, calculated_data_uncategorized

    @Transactional(propagation=Propagation.REQUIRED)
    def update_pareto(self, user_id, transaction_id, is_bulk, pareto_data, **inputs):

        if is_bulk:
            if not pareto_data:
                raise exceptions.BadRequest("pareto_data is required when 'is_bulk' is set")

            for pareto in pareto_data:
                data_detail = data_detail_repository.get_by_uuid(pareto["detail_id"])
                if not data_detail:
                    raise exceptions.NotFound("Data Detail not found")
                data_detail_repository.update(
                    data_detail,
                    {
                        "deviasi": (
                            pareto["deviasi"]
                            if "deviasi" in pareto
                            else data_detail.deviasi
                        ),
                        "persen_hr": (
                            pareto["persen_hr"]
                            if "persen_hr" in pareto
                            else data_detail.persen_hr
                        ),
                        "updated_by": user_id,
                    },
                )

        else:
            data_detail = self.data_detail_repository.get_by_uuid(inputs["detail_id"])
            if not data_detail:
                raise exceptions.NotFound("Data Detail not found")

            self.data_detail_repository.update(
                data_detail,
                {
                    "deviasi": (
                        inputs["deviasi"]
                        if "deviasi" in inputs
                        else data_detail.deviasi
                    ),
                    "persen_hr": (
                        inputs["persen_hr"]
                        if "persen_hr" in inputs
                        else data_detail.persen_hr
                    ),
                    "updated_by": user_id,
                },
            )

        return data_detail if not is_bulk else None


data_pareto_controller = DataParetoController()
