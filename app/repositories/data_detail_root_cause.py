from typing import Optional

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail,
    EfficiencyDataDetailRootCause,
    EfficiencyTransaction,
    Variable,
)
from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import joinedload

from core.repository import BaseRepository


class DataDetailRootCauseRepository(BaseRepository[EfficiencyDataDetailRootCause]):
    pass
