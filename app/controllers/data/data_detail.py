from collections import defaultdict

from digital_twin_migration.database import Propagation, Transactional, db
from flask_restful import Resource
from flask_restful.reqparse import Argument
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyTransaction)


from app.repositories.data_detail import DataDetailRepository
from app.schemas import EfficiencyDataDetailSchema, VariableSchema
from core.controller.base import BaseController
from core.security import token_required
from core.utils import (calculate_gap, calculate_persen_losses, parse_params,
                        response, calculate_pareto)

from core.cache import Cache

variable_schema = VariableSchema()
data_details_schema = EfficiencyDataDetailSchema()
data_detail_repository = DataDetailRepository(EfficiencyDataDetail)


class DataDetailController(BaseController[EfficiencyDataDetail]):
    def __init__(self, data_detail_repository: DataDetailRepository = data_detail_repository):
        super().__init__(model=EfficiencyTransaction, repository=data_detail_repository)
        self.data_detail_repository = data_detail_repository

    def get_data_pareto(self, transaction_id, percent_threshold):

        # Calculate total biaya for the transaction
        pareto_cache_data = Cache.get_by_key(f"data_pareto::{transaction_id}")
        result = []
        total_persen = 0

        if pareto_cache_data:
            calculated_data_by_category, aggregated_persen_losses = pareto_cache_data

            for category, losses in aggregated_persen_losses.items():
                total_persen += losses
                if percent_threshold and total_persen >= percent_threshold:
                    break

                result.append(
                    {
                        "category": category,
                        "total_persen_losses": losses,
                        "total_nilai_losses": (losses / 100) * 1000,
                        "data": calculated_data_by_category[category],
                    }
                )
            return result

        data = data_detail_repository.get_data_pareto(transaction_id)
        # target_data = data_detail_repository.get_data_pareto(transaction_id, False)

        if data is None:
            return response(404, False, "Data is not available")

        calculated_data_by_category = defaultdict(list)
        aggregated_persen_losses = defaultdict(float)

        for current_data, target_data, total_cost in data:
            gap, persen_losses, nilai_losses = calculate_pareto(target_data, current_data)

            category = current_data.variable.category
            aggregated_persen_losses[category] += persen_losses or 0

            calculated_data_by_category[category].append(
                {
                    "id": current_data.id,
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
                }
            )

            # Sort aggregated losses only once, limit looping
            aggregated_persen_losses = dict(
                sorted(aggregated_persen_losses.items(), key=lambda x: x[1], reverse=True)
            )

            Cache.set_cache((calculated_data_by_category, aggregated_persen_losses), f"data_pareto::{transaction_id}")

            for category, losses in aggregated_persen_losses.items():
                total_persen += losses
                if percent_threshold and total_persen >= percent_threshold:
                    break

                result.append(
                    {
                        "category": category,
                        "total_persen_losses": losses,
                        "total_nilai_losses": (losses / 100) * 1000,
                        "data": calculated_data_by_category[category],
                    }
                )
        return result


data_detail_controller = DataDetailController()