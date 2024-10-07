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

    def get_by_detail_id(self, detail_id: str, is_repair: bool = False):
        query = self._query({'members', 'actions'})
        query = query.filter(EfficiencyDataDetailRootCause.data_detail_id == detail_id, EfficiencyDataDetailRootCause.is_repair.is_(is_repair))
        return self._all_unique(query)

    def get_by_detail_id_parent_ids(self, parent_ids: list, detail_id: str):
        if not parent_ids:
            return (
                []
            )  # Or handle the case as needed (e.g., return None or raise an exception)

        # Construct the base query
        query = self._query()

        # Apply filters
        query = query.filter(
            and_(
                EfficiencyDataDetailRootCause.data_detail_id == detail_id,
                EfficiencyDataDetailRootCause.parent_cause_id.in_(parent_ids),
            )
        )

        # Retrieve unique records (assuming _all_unique applies distinct or similar)
        return self._all_unique(query)

    def get_by_root_ids(self, root_ids: list):
        query = self._query({'actions'})
        query = query.filter(EfficiencyDataDetailRootCause.id.in_(root_ids))
        return self._all_unique(query)


    def _join_members(self, query: Select) -> Select:
        return query.options(joinedload(EfficiencyDataDetailRootCause.members))

    def _join_actions(self, query: Select) -> Select:
        return query.options(joinedload(EfficiencyDataDetailRootCause.actions))

    def get_by_detail_id_with_actions(self, detail_id: str):
        query = self._query()

    def delete_bulk(self, root_causes: list):
        for root_cause in root_causes:
            self.delete(root_cause)

    def delete_members(self, roots):
        for root in roots.values():
            for member in root.members:
                self.delete(member)

    def delete_actions(self, roots:list):
        for root in roots.values():
            for action in root.actions:
                self.delete(action)
