from typing import Optional

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyDataDetailRootCause, EfficiencyTransaction,
    Variable, EfficiencyDataDetailRootCauseMember, VariableCause)
from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import joinedload,selectinload, aliased

from core.repository import BaseRepository


class DataDetailRootCauseRepository(BaseRepository[EfficiencyDataDetailRootCause]):

    def get_by_detail_id(self, detail_id: str, is_repair: bool = False):
        query = self._query()
        query = query.filter(EfficiencyDataDetailRootCause.data_detail_id == detail_id)
        
        query = query.options(selectinload(EfficiencyDataDetailRootCause.members))
        query = query.options(selectinload(EfficiencyDataDetailRootCause.actions))
        
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
        
        query = query.options(selectinload(EfficiencyDataDetailRootCause.members))
        query = query.options(selectinload(EfficiencyDataDetailRootCause.actions))
        query = query.options(selectinload(EfficiencyDataDetailRootCause.parent_cause))

        # Retrieve unique records (assuming _all_unique applies distinct or similar)
        return self._all_unique(query)
    
    def get_total_root_cause_by_detail_ids(self, details_ids:list):
        dd = aliased(EfficiencyDataDetail)
        rc = aliased(EfficiencyDataDetailRootCause)
        rcm = aliased(EfficiencyDataDetailRootCauseMember)
        vc = aliased(VariableCause)
        
        query = (
            self.session.query(
                dd.id.label('data_details_id'),
                dd.variable_id.label('variable_id'),
                rcm.is_repair.label('is_repair'),
                rcm.is_checked.label('is_checked'),
                vc.name.label("variable_cause_name"),
                vc.id.label("variable_cause_id"),
            )
            .join(rc, dd.root_causes)
            .join(rcm, and_(rc.id == rcm.root_cause_id, rc.data_detail_id == dd.id))
            .join(vc, rcm.cause_id == vc.id)
            .filter(dd.id.in_(details_ids))
        )

        # Execute the query and return the results
        return query.all()
    
    
    def get_by_root_ids(self, root_ids: list):
        query = self._query()
        query = query.filter(EfficiencyDataDetailRootCause.parent_cause_id.in_(root_ids))
        
        query = query.options(selectinload(EfficiencyDataDetailRootCause.actions))
        return self._all_unique(query)


    def get_by_member_id_and_detail_id(self, cause_id: str, detail_id: str):
        query = self._query().join(EfficiencyDataDetailRootCause.members)
        query = query.filter(
            and_(
                EfficiencyDataDetailRootCauseMember.cause_id == cause_id,
                EfficiencyDataDetailRootCause.data_detail_id == detail_id,
            )
        )

        query = query.options(selectinload(EfficiencyDataDetailRootCause.members))
        query = query.options(selectinload(EfficiencyDataDetailRootCause.actions))
        query = query.options(selectinload(EfficiencyDataDetailRootCause.parent_cause))
        
        return self._first(query)

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
