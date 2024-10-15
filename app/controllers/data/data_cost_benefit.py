
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from os import cpu_count
from core.controller.base import BaseController
from core.cache import cache_flask
from core.factory import data_detail_factory
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail)
from werkzeug import exceptions
from core.factory import data_factory, variable_factory
from core.utils.formula import calculate_cost_benefit, calculate_gap, calculate_persen_losses

from app.controllers.data.data_root_cause import data_detail_root_cause_controller

data_detail_repository = data_detail_factory.data_detail_repository
data_repository = data_factory.data_repository
variable_schema = variable_factory.variable_schema


class DataCostBenefit(BaseController):

    def __init__(self, data_detail_repository=data_detail_repository):
        super().__init__(model=EfficiencyDataDetail, repository=data_detail_repository)
        self.data_detail_repository = data_detail_repository

    def get_cost_benefit_data(self, transaction_id, cost_threshold=None):
        result_pareto = []
        total_persen = 0
        total_biaya = 0
        total_cost_benefit = 0

        @cache_flask.cached(key_prefix=f"data_pareto_{transaction_id}")
        def get_data(transaction_id):
            categorized_data = data_detail_repository.get_data_pareto(transaction_id)
            nphr = data_detail_repository.get_data_nphr(transaction_id).nilai

            return categorized_data, nphr

        categorized_data, nphr = get_data(transaction_id)
        
        actions_all_detail = data_detail_root_cause_controller.check_root_cause(transaction_id)
        
        if categorized_data is None:
            raise exceptions.NotFound("Data not found")

        def batch_process_data(categorized_data):
            result = []
            aggregated = {
                'persen_losses': 0,
                'total_biaya': 0,
                'cost_benefit': 0,
                'nilai_losses': 0
            }
            for current_data, target_data, total_cost in categorized_data:
                gap = calculate_gap(target_data.nilai, current_data.nilai)
                persen_losses = calculate_persen_losses(
                    gap, target_data.deviasi, current_data.persen_hr
                )
                nilai_losses = (persen_losses / 100) * 1000

                hasCause = True
                
                category = current_data.variable.category
                
                actions = actions_all_detail.get(current_data.id, [])

                # Static Data
                netto = 1000

                cost_benefit = calculate_cost_benefit(netto, nphr, nilai_losses)
                
                if category is not None:
                    aggregated['persen_losses'] += persen_losses or 0
                    aggregated['total_biaya'] += total_cost or 0
                    aggregated['cost_benefit'] += cost_benefit or 0
                    aggregated['nilai_losses'] += nilai_losses or 0
                

                payload = {
                    "id": str(current_data.id),
                    "variable": variable_schema.dump(current_data.variable),
                    "existing_data": current_data.nilai,
                    "reference_data": target_data.nilai,
                    "deviasi": current_data.deviasi,
                    "persen_hr": current_data.persen_hr,
                    "persen_losses": persen_losses,
                    "nilai_losses": nilai_losses,
                    "cost_benefit": cost_benefit,
                    "gap": gap,
                    "total_biaya": total_cost,
                    "symptoms": "Higher" if gap > 0 else "Lower",
                    "has_cause" : hasCause,
                    "is_pareto" : current_data.variable.is_pareto,
                    "action_menutup_gap": actions
                }

                result.append(payload) if category is not None else None

            return result, aggregated

        with ThreadPoolExecutor(max_workers=cpu_count()) as executor:
            data_future = executor.submit(batch_process_data, categorized_data)
            results, aggregated = data_future.result()

        def calc_ratio(item):
            cost = item.get('total_biaya')
            if cost is None or cost == 0:
                return float('inf') if item['cost_benefit'] > 0 else 0
            return item['cost_benefit'] / cost

        known_cost_items = [item for item in results if item.get('total_biaya') > 0]
        unknown_cost_items = [item for item in results if item.get('total_biaya') == 0]

        # Sort items with known costs by ratio
        sorted_known_cost_items = sorted(known_cost_items, key=calc_ratio, reverse=True)

        # Sort items with unknown costs by potential benefit
        sorted_unknown_cost_items = sorted(unknown_cost_items, key=lambda x: x['cost_benefit'], reverse=True)

        result = []
        cumulative_cost = 0
        
        if not cost_threshold:
            cost_threshold = aggregated['total_biaya']

        # Add items with known costs up to the threshold
        for item in sorted_known_cost_items:

            
            if (cost_threshold > 0) and (cumulative_cost + item['total_biaya'] <= cost_threshold):
                result.append(item)
                cumulative_cost += item['total_biaya']
            else:
                if cost_threshold == 0:
                    result.append(item)
                break

        # Add all items with unknown costs
        result.extend(sorted_unknown_cost_items)

        return result, aggregated['persen_losses'], aggregated['nilai_losses'], aggregated['total_biaya'], aggregated['cost_benefit'], cost_threshold


data_cost_benefit_controller = DataCostBenefit()
