""" Defines the Cases repository """

from typing import Optional

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import (EfficiencyDataDetail,
                                                          Variable, EfficiencyTransaction, EfficiencyDataDetailRootCause)
from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import joinedload

from core.repository import BaseRepository


class DataDetailRepository(BaseRepository[EfficiencyDataDetail]):

    def get_by_data_id_and_variable_type(self, data_id: str, type: str):
        query = self._query({'variable'})
        query = query.filter(
            and_(
                EfficiencyDataDetail.efficiency_transaction_id == data_id,
                Variable.in_out == type,
            )
        )
        return self._all_unique(query)

    def get_by_uuid(self, uuid: str, join_: set[str] | None = None):
        query = self._query(join_)
        query = query.filter(EfficiencyDataDetail.id == uuid)

        if join_ is not None:
            return self.all_unique(query)
        return self._one_or_none(query)

    def _join_variable(self, query: Select) -> Select:
        return query.join(Variable)

    def get_data_pareto(self, data_id: str, with_total_cost: bool = False):
        if with_total_cost:
            query = db.session.query(EfficiencyDataDetail, EfficiencyDataDetail.total_cost()).join(EfficiencyTransaction).join(Variable).filter(and_(
                EfficiencyDataDetail.efficiency_transaction_id == data_id,
                Variable.in_out == "out",
            )).all()
            
            return query
        
        else:
            query = select(self.model_class)
            query = self._maybe_join(query, {'variable', 'data'})
            query = query.filter(and_(
                EfficiencyTransaction.jenis_parameter == "Target",
                Variable.in_out == "out",
            ))
            return self._all(query)
    
    
    def _join_data(self, query: Select) -> Select:
        return query.join(EfficiencyTransaction)
    
    def _join_root_cause(self, query: Select) -> Select:
        return query.join(EfficiencyDataDetailRootCause)