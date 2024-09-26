

from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyTransaction)

from core.controller.base import BaseController
from core.factory import data_factory, data_detail_factory
from werkzeug.exceptions import HTTPException
from core.config import config
from app.controllers.data import data_pareto_controller


class DataNphrController(BaseController[EfficiencyTransaction]):
    def __init__(self):
        super().__init__(EfficiencyTransaction, data_factory.data_repository)
        self.data_repository = data_factory.data_repository
        self.data_detail_repository = data_detail_factory.data_detail_repository

    def get_data_nphr(self, data_id: str = None) -> EfficiencyDataDetail:
        data = self.data_repository.get_newest_data() if data_id is None else self.data_repository.get_by_uuid(data_id)

        if not data:
            raise HTTPException(description="Data not found", response=404)

        current_nphr = self.data_detail_repository.get_data_nphr(data.id)
        target_nphr = self.data_detail_repository.get_data_nphr(is_target=True)
        kpi_nphr = self.data_detail_repository.get_data_nphr(is_kpi=True)

        nphr = {
            "current": current_nphr.nilai if current_nphr else None,
            "target": target_nphr.nilai if target_nphr else None,
            "kpi": kpi_nphr.nilai if kpi_nphr else None,
        }

        if config.ENVIRONMENT == "development":
            nphr["kpi"] = 12352.98952565403
            nphr["target"] = 2352.98952565403

        # get data chart pareto
        data_pareto = data_pareto_controller.get_data_pareto(data.id, data.persen_threshold)

        return data_pareto[1], nphr, data.id


data_nphr_controller = DataNphrController()
