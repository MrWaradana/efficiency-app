""" Defines the Excels repository """

from typing import Optional
from uuid import UUID

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import Excel
from sqlalchemy.orm.query import Query

from core.repository import BaseRepository


class ExcelsRepository(BaseRepository[Excel]):

    def get_by_uuid(self, uuid: str, join_: set[str] | None = None):
        query = self._query(join_)
        query = query.filter(Excel.id == uuid)

        if join_ is not None:
            return self._all_unique(query)

        return self._one_or_none(query)
