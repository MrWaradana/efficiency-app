""" Defines the Cases repository """

from typing import Optional

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyDataDetailRootCause, EfficiencyTransaction,
    Variable)
from sqlalchemy import Select, and_, func, select
from sqlalchemy.orm import joinedload

from core.repository import BaseRepository
from core.config import config



class DataDetailRepository(BaseRepository[EfficiencyDataDetail]):

    def get_by_data_id_and_variable_type(self, data_id: str, type: str):
        query = self._query({"variable"})
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

    def get_data_pareto(self, data_id: str):
        query = (
            db.session.query(EfficiencyDataDetail, EfficiencyDataDetail.total_cost())
            .join(EfficiencyTransaction)
            .join(Variable)
        )

        current_query = query.filter(
            and_(
                EfficiencyDataDetail.efficiency_transaction_id == data_id,
                Variable.in_out == "out",
            )
        ).all()

        target_query = query.filter(
            and_(
                EfficiencyTransaction.jenis_parameter == "target",
                Variable.in_out == "out",
            )
        ).all()

        target_mapping = {item.variable_id: item for item, total_cost in target_query}

        paired_data = []
        for current_item, total_cost in current_query:
            if current_item.variable_id in target_mapping:
                paired_data.append(
                    (current_item, target_mapping[current_item.variable_id], total_cost)
                )

        return paired_data

    def get_data_nphr(self, data_id: str = None, is_target: bool = False, is_kpi: bool = False):
        query = self._query({"variable", "data"})
        nphr_input_name = config.NPHR_VARIABLE_NAME

        if is_target or is_kpi:
            query = query.filter(
                and_(
                    EfficiencyTransaction.jenis_parameter == ("target" if is_target else "kpi"),
                    Variable.input_name == nphr_input_name,
                    EfficiencyDataDetail.nilai.isnot(None),
                )
            )

        else:
            query = query.filter(
                and_(
                    EfficiencyDataDetail.efficiency_transaction_id == data_id,
                    Variable.input_name == nphr_input_name,
                )
            )

        return self._one_or_none(query)

    def _join_data(self, query: Select) -> Select:
        return query.join(EfficiencyTransaction)

    def _join_root_cause(self, query: Select) -> Select:
        return query.join(EfficiencyDataDetailRootCause)
