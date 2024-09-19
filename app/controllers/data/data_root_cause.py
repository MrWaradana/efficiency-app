

from core.controller.base import BaseController
from digital_twin_migration.models.efficiency_app import EfficiencyDataDetailRootCause
from core.factory import data_detail_root_cause_factory
from core.cache import Cache
from werkzeug import exceptions as exc
from digital_twin_migration.database import Propagation, Transactional


class DataDetailRootCauseController(BaseController[EfficiencyDataDetailRootCause]):
    def __init__(self, data_detail_root_cause_repository=data_detail_root_cause_factory.data_detail_root_cause_repository):
        super().__init__(model=EfficiencyDataDetailRootCause, repository=data_detail_root_cause_repository)
        self.data_detail_root_cause_repository = data_detail_root_cause_repository

    def get_by_detail_id(self, detail_id):
        @Cache.cached(f"data_detail_root_cause_{detail_id}")
        def fetch_data_detail_root_cause():
            root_causes = self.data_detail_root_cause_repository.get_by_detail_id(detail_id)

            return root_causes

        return fetch_data_detail_root_cause()

    @Transactional(propagation=Propagation.REQUIRED)
    def create_data_detail_root_cause(self, user_id, transaction_id, detail_id, is_bulk, data_root_causes, **inputs):
        if is_bulk:
            if not data_root_causes:
                return exc.BadRequest("Data root causes must be provided if is_bulk is True")

            root_cause_ids = [root_cause["cause_id"] for root_cause in data_root_causes]

            data_roots = self.data_detail_root_cause_repository.get_by_detail_id_cause_ids(root_cause_ids, detail_id)

            if data_roots:
                self.data_detail_root_cause_repository.delete_bulk(data_roots)

            data_root_causes_records = [
                EfficiencyDataDetailRootCause(
                    data_detail_id=detail_id,
                    cause_id=root_cause["cause_id"],
                    is_repair=(
                        root_cause["is_repair"] if "is_repair" in root_cause else False
                    ),
                    biaya=root_cause["biaya"] if "biaya" in root_cause else 0,
                    variable_header_value=(
                        root_cause["variable_header_value"]
                        if "variable_header_value" in root_cause
                        else None
                    ),
                    created_by=user_id,
                )
                for root_cause in data_root_causes
            ]
            
            self.data_detail_root_cause_repository.create_bulk(data_root_causes_records)

        else:
            missing_input = next(
                (name for name, input in inputs.items() if not input), None
            )
            if missing_input:
                return exc.BadRequest(f"'{missing_input}' is required when 'is_bulk' is not set")

            self.data_detail_root_cause_repository.create(
                {**inputs, "data_detail_id": detail_id, "created_by": user_id}
            )

        Cache.remove_by_prefix(f"data_detail_root_cause_{detail_id}")

        return None


data_detail_root_cause_controller = DataDetailRootCauseController()
