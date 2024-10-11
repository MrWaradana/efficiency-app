

from core.controller.base import BaseController
from core.cache import cache_flask
from core.factory import data_detail_factory
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail)
from werkzeug import exceptions

data_detail_repository = data_detail_factory.data_detail_repository


class DataEngineFlowController(BaseController):

    def __init__(self, data_repository=data_detail_repository):
        super().__init__(model=EfficiencyDataDetail, repository=data_repository)
        self.data_detail_repository = data_detail_repository

    def get_all_engine_flow_data(self, data_id):
        @cache_flask.cached(key_prefix=f"data_engine_flow_{data_id}")
        def fetch_data(data_id):
            # Try to get data from cache, otherwise fetch from repository
            cache_key = f"data_details_{data_id}_out"
            data_details = cache_flask.get(cache_key) or self.data_detail_repository.get_by_data_id_and_variable_type(data_id, "out")
        
            
            if not data_details:
                raise exceptions.NotFound("Data Details not found")

            # Create a mapping from excel variable names
            data_details_mapping = {data_detail.variable.excel_variable_name: data_detail.nilai for data_detail in data_details}

            # Required variables to fetch
            variables = [
                "Plant gross power",  # EG
                "ST Assembly [1] - HPT: ST Group [1] - HPT-1: Group overall efficiency",
                "ST Assembly [1] - HPT: ST Group [2] - HPT-2: Group overall efficiency",
                "ST Assembly [1] - HPT: ST Group [58] - HPT-3: Group overall efficiency",
                "ST Assembly [2] - IPT: ST Group [3] - IPT-1: Group overall efficiency",
                "ST Assembly [2] - IPT: ST Group [4] - IPT-2: Group overall efficiency",
                "ST Assembly [3] - LPT: ST Group [5] - LPT-1: Group overall efficiency",
                "ST Assembly [3] - LPT: ST Group [6] - LPT-2: Group overall efficiency",
                "ST Assembly [3] - LPT: ST Group [7] - LPT-3: Group overall efficiency",
                "ST Group [60] - LPT-4: Group overall efficiency",
                "TTD HPH 7",  # RH7
                "TTD HPH 6",  # RH6
                "TTD HPH 5",  # RH5
                "TTD LPH 1",  # RH1
                "TTD LPH 2",  # RH2
                "TTD LPH 3"   # RH3
            ]

            # Fetch all the required variables at once
            results = {var: data_details_mapping.get(var, None) for var in variables}

            # Return variables of interest with each RH as individual keys
            return {
                'EG': results.get("Plant gross power"), ## MW
                'HPT': (results.get(variables[1]) * results.get(variables[2]) * results.get(variables[2]))/100^3, #% 
                'IPT': (results.get(variables[4]) * results.get(variables[5]))/100^2, #%
                'LPT': (results.get(variables[6]) * results.get(variables[7]) * results.get(variables[8]) * results.get(variables[9]))/100^4,
                'RH7': results.get("TTD HPH 7"),
                'RH6': results.get("TTD HPH 6"),
                'RH5': results.get("TTD HPH 5"),
                'RH1': results.get("TTD LPH 1"),
                'RH2': results.get("TTD LPH 2"),
                'RH3': results.get("TTD LPH 3")
            }
            
        return fetch_data(data_id)

data_engine_flow_controller = DataEngineFlowController()