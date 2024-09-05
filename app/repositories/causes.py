""" Defines the Cases repository """

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail,
    EfficiencyDataDetailRootCause,
    VariableCause,
)
from sqlalchemy import Select
from sqlalchemy.orm import contains_eager, joinedload

from core.repository import BaseRepository


class CausesRepository(BaseRepository[VariableCause]):

    def get_by_variable_id(
        self, variable_id: str, join_: set[str] | None = None
    ) -> list[VariableCause]:

        query = self._query(join_)
        query = query.filter(VariableCause.variable_id == variable_id)
        query = query.filter(VariableCause.parent_id == None)

        if join_ is not None:
            return self._all_unique(query)

        return self._all(query)

    def _join_variable(self, query: Select) -> Select:
        return query.options(joinedload(VariableCause.variable))

    def _join_children(self, query: Select) -> Select:
        return query.options(joinedload(VariableCause.children))

    def _join_root_causes(self, query: Select) -> Select:
        return query.options(joinedload(VariableCause.root_causes))

    def get_by_uuid(self, uuid: str, join_: set[str] | None = None):
        query = self._query(join_)
        query = query.filter(VariableCause.id == uuid)

        if join_ is not None:
            return self._all_unique(query)

        return self._one_or_none(query)
