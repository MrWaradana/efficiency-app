from typing import Optional

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyDataDetailRootCause, EfficiencyTransaction,
    Variable)
from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import joinedload

from core.repository import BaseRepository


class DataDetailRootCauseRepository(BaseRepository[EfficiencyDataDetailRootCause]):

    def get_by_detail_id(self, detail_id: str):
        query = self._query()
        query = query.filter(EfficiencyDataDetailRootCause.data_detail_id == detail_id)
        return self._all_unique(query)

    def get_by_detail_id_cause_ids(self, cause_ids: list, detail_id: str):
        if not cause_ids:
            return []  # Or handle the case as needed (e.g., return None or raise an exception)

        # Construct the base query
        query = self._query()

        # Apply filters
        query = query.filter(
            and_(
                EfficiencyDataDetailRootCause.data_detail_id == detail_id,
                EfficiencyDataDetailRootCause.cause_id.in_(cause_ids)
            )
        )

        # Retrieve unique records (assuming _all_unique applies distinct or similar)
        return self._all_unique(query)

    def delete_bulk(self, root_causes: list):
        for root_cause in root_causes:
            self.delete(root_cause)
