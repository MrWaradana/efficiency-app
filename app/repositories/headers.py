""" Defines the VariableHeaders repository """

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import VariableHeader
from sqlalchemy import Select
from sqlalchemy.orm import joinedload

from core.repository import BaseRepository


class HeadersRepository(BaseRepository[VariableHeader]):
    def get_by_variable_id(
        self, variable_id: str, join_: set[str] | None = None
    ) -> list[VariableHeader]:

        query = self._query(join_)
        query = query.filter(VariableHeader.variable_id == variable_id)

        if join_ is not None:
            return self._all_unique(query)

        return self._all(query)

    def get_by_uuid(self, uuid: str, join_: set[str] | None = None):
        query = self._query(join_)
        query = query.filter(VariableHeader.id == uuid)

        if join_ is not None:
            return self._all_unique(query)

        return self._one_or_none(query)

    def _join_variable(self, query: Select) -> Select:
        return query.options(joinedload(VariableHeader.variable))
