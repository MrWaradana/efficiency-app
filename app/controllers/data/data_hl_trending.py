from core.controller.base import BaseController
from digital_twin_migration.models.efficiency_app import EfficiencyTransaction
from core.factory import data_factory
from core.utils import calculate_pareto

data_schema = data_factory.exclude_schema(["efficiency_transaction_details"])


class DataTrendingController(BaseController[EfficiencyTransaction]):
    def __init__(self, data_repository=data_factory.data_repository):
        super().__init__(model=EfficiencyTransaction, repository=data_repository)
        self.data_repository = data_repository

    def get_trending_data(self, start_date, end_date, variable_ids):
        # check if variable id contains (,)
        if ',' in variable_ids:
            variable_ids_list = variable_ids.split(',')
        else:
            variable_ids_list = [variable_ids]

        data = self.data_repository.get_data_trending(start_date, end_date, variable_ids_list)
        data_target = self.data_repository.get_target_data_by_variable(variable_ids_list)

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
                    "variable_id": current_detail.variable_id,
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


data_trending_controller = DataTrendingController()
