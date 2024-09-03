""" Defines the Cases repository """

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import Case

from core.repository import BaseRepository


class CasesRepository(BaseRepository[Case]):

    def get_by_name(self, name: str, join_: set[str] | None = None):
        query = self._query(join_)
        query = query.filter(Case.name == name)

        if join_ is not None:
            return self._all_unique(query)

        return self._one_or_none(query)

    def get_by_uuid(self, uuid: str, join_: set[str] | None = None):
        query = self._query(join_)
        query = query.filter(Case.id == uuid)

        if join_ is not None:
            return self._all_unique(query)

        return self._one_or_none(query)
