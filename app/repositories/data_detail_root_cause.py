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
        query = self._query({"variable", "cause"})
        query = query.filter(EfficiencyDataDetailRootCause.data_detail_id == detail_id)
        return self._all_unique(query)
