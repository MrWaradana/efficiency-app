""" Defines the Variable repository """

from typing import List

from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import Variable
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.query import Query

from core.repository import BaseRepository


class VariablesRepository(BaseRepository[Variable]):
    def get_by_uuid(self, uuid: str, join_: set[str] | None = None):
        query = self._query(join_)
        query = query.filter(Variable.id == uuid)

        if join_ is not None:
            return self._all_unique(query)

        return self._one_or_none(query)

    def get_by_excel_id(self, excel_id: str, join_: set[str] | None = None):
        query = self._query(join_)
        query = query.filter(Variable.excel_id == excel_id)

        if join_ is not None:
            return self._all_unique(query)

        return self._all(query)
