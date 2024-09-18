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

variable_schema = VariableSchema()
data_details_schema = EfficiencyDataDetailSchema()
data_detail_repository = DataDetailRepository(EfficiencyDataDetail)


class DataDetailController(BaseController[EfficiencyDataDetail]):
    def __init__(
        self, data_detail_repository: DataDetailRepository = data_detail_repository
    ):
        super().__init__(model=EfficiencyTransaction, repository=data_detail_repository)
        self.data_detail_repository = data_detail_repository

    @Transactional(propagation=Propagation.REQUIRED)
    def get_data_pareto(self, transaction_id, percent_threshold):
        # Calculate total biaya for the transaction
        # pareto_cache_data = Cache.get_by_prefix(
        #     f"data_calculated_data_by_category_{transaction_id}"
        # )
        result_pareto = []
        result_chart = []
        total_persen = 0

        # if pareto_cache_data:
        #     # raise Exception(pareto_cache_data['aggregated_persen_losses'], "cachheheheh")
        #     for category, losses in pareto_cache_data['aggregated_persen_losses'].items():
        #         total_persen += losses
        #         if percent_threshold and total_persen >= percent_threshold:
        #             break

        #         result.append(
        #             {
        #                 "category": category,
        #                 "total_persen_losses": losses,
        #                 "total_nilai_losses": (losses / 100) * 1000,
        #                 "data": pareto_cache_data['data'][category],
        #             }
        #         )

        #     return result
        transaction_data = data_repository.get_by_uuid(transaction_id)
        if not transaction_data:
            raise Exception("Transaction data not found")

        data = data_detail_repository.get_data_pareto(transaction_id)

        if data is None:
            raise Exception("Transaction data not found")

        calculated_data_by_category = defaultdict(list)
        aggregated_persen_losses = defaultdict(float)

        for current_data, target_data, total_cost in data:
            gap = calculate_gap(target_data.nilai, current_data.nilai)
            persen_losses = calculate_persen_losses(
                gap, target_data.deviasi, current_data.persen_hr
            )
            nilai_losses = (persen_losses / 100) * 1000

            category = current_data.variable.category
            aggregated_persen_losses[category] += persen_losses or 0
            hasCause = True if current_data.variable.causes else False

            calculated_data_by_category[category].append(
                {
                    "id": str(current_data.id),
                    "variable": variable_schema.dump(current_data.variable),
                    "existing_data": current_data.nilai,
                    "reference_data": target_data.nilai,
                    "deviasi": current_data.deviasi,
                    "persen_hr": current_data.persen_hr,
                    "persen_losses": persen_losses,
                    "nilai_losses": nilai_losses,
                    "gap": gap,
                    "total_biaya": total_cost,
                    "symptoms": "Higher" if gap > 0 else "Lower",
                    "has_cause" : hasCause
                }
            )

        # Sort aggregated losses only once, limit looping
        aggregated_persen_losses = dict(
            sorted(aggregated_persen_losses.items(), key=lambda x: x[1], reverse=True)
        )

        # total_persen_losses = sum(aggregated_persen_losses.values())
        # total_nilai_losses = sum([(losses / 100) * 1000 for losses in aggregated_persen_losses.values()])

        for category, losses in aggregated_persen_losses.items():
            total_persen += losses

            result_chart.append(
                {
                    "category": category,
                    "total_persen_losses": losses,
                    "total_nilai_losses": (losses / 100) * 1000,
                }
            )

            if percent_threshold and total_persen >= percent_threshold:
                total_persen -= losses
                break

            sorted_calculated_data = sorted(
                calculated_data_by_category[category],
                key=lambda x: x["persen_losses"],
                reverse=True,
            )

            result_pareto.append(
                {
                    "category": category,
                    "total_persen_losses": losses,
                    "total_nilai_losses": (losses / 100) * 1000,
                    "data": sorted_calculated_data,
                }
            )

        # update persen_threshold
        transaction_data.persen_threshold = percent_threshold

        total_losses = (total_persen / 100) * 1000

        return result_pareto, aggregated_persen_losses, total_persen, total_losses, transaction_data.persen_threshold if transaction_data.persen_threshold else percent_threshold


data_detail_controller = DataDetailController()
