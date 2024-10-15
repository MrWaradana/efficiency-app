""" Defines the Cases repository """

from typing import Optional

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyDataDetailRootCause, EfficiencyTransaction,
    Variable)
from sqlalchemy import Select, and_, case, func, select, or_, union_all
from sqlalchemy.orm import joinedload, aliased, selectinload, subqueryload

from core.repository import BaseRepository
from core.config import config
from werkzeug import exceptions


class DataDetailRepository(BaseRepository[EfficiencyDataDetail]):

    def get_by_data_id_and_variable_type(self, data_id: str, type: str, is_categorized: bool = False):
        query = self._query({"variable"})
        query = query.filter(
            and_(
                EfficiencyDataDetail.efficiency_transaction_id == data_id,
                Variable.in_out == type,
            )
        )

        if is_categorized:
            query = query.filter(
                Variable.category.isnot(None)
            )

        query = query.options(joinedload(EfficiencyDataDetail.variable))
        query = query.options(joinedload(EfficiencyDataDetail.efficiency_transaction))
        return self._all_unique(query)

    def get_by_uuid(self, uuid: str, join_: set[str] | None = None):
        query = self._query(join_)
        query = query.filter(EfficiencyDataDetail.id == uuid)

        if join_ is not None:
            return self.all_unique(query)
        return self._one_or_none(query)

    def _join_variable(self, query: Select) -> Select:
        return query.join(Variable)

    # def get_data_pareto(self, data_id: str, is_uncategorized: bool = False):
    #     # Create a subquery for the target data to reduce number of queries
    #     target_subquery = (
    #         db.session.query(EfficiencyTransaction.id)
    #         .filter_by(jenis_parameter="Commision")
    #         .scalar_subquery()
    #     )

    #     # Use select_from to establish the join relationship once
    #     base_query = (
    #         db.session.query(
    #             EfficiencyDataDetail,
    #             EfficiencyDataDetail.total_cost(),
    #             Variable.id.label('variable_id')  # Include variable_id in main query
    #         )
    #         .select_from(EfficiencyDataDetail)
    #         .join(Variable)
    #         .filter(
    #             Variable.in_out == "out",
    #             or_(
    #                 Variable.is_pareto.is_(True),
    #                 Variable.category.isnot(None)
    #             )
    #         )
    #         .options(
    #             joinedload(EfficiencyDataDetail.variable),  # Eager load relationships
    #             joinedload(EfficiencyDataDetail.efficiency_transaction)
    #         )
    #     )

    #    # Execute both queries in parallel using union
    #     combined_query = db.session.query(
    #         EfficiencyDataDetail,
    #         EfficiencyDataDetail.total_cost(),
    #         Variable.id.label('variable_id')
    #     ).select_from(
    #         union_all(
    #             base_query.filter(EfficiencyDataDetail.efficiency_transaction_id == data_id),
    #             base_query.filter(EfficiencyDataDetail.efficiency_transaction_id == target_subquery)
    #         ).alias('combined')
    #     )

    #     # Group results by transaction type
    #     results = combined_query.all()
    #     if not results:
    #         raise exceptions.NotFound("No data found")

    #     # Separate current and target results
    #     current_results = []
    #     target_mapping = {}

    #     for detail, total_cost, var_id in results:
    #         if detail.efficiency_transaction_id == data_id:
    #             current_results.append((detail, total_cost, var_id))
    #         else:
    #             target_mapping[var_id] = detail

    #     # Match pairs more efficiently
    #     paired_data = [
    #         (current, target_mapping[var_id], total_cost)
    #         for current, total_cost, var_id in current_results
    #         if var_id in target_mapping
    #     ]

    #     return paired_data

    # def get_data_pareto(self, data_id: str, is_uncategorized: bool = False):
    #     query = (
    #         db.session.query(EfficiencyDataDetail, EfficiencyDataDetail.total_cost())
    #         .join(EfficiencyTransaction)
    #         .join(Variable)
    #     )

    #     current_query = query.filter(
    #         and_(
    #             EfficiencyDataDetail.efficiency_transaction_id == data_id,
    #             Variable.in_out == "out",

    #         ),
    #         or_(
    #             Variable.is_pareto.is_(True),
    #             Variable.category.isnot(None)
    #         )
    #     ).all()

    #     target = EfficiencyTransaction.query.filter_by(jenis_parameter="Commision").first()

    #     target_query = query.filter(
    #         and_(
    #             EfficiencyDataDetail.efficiency_transaction_id == target.id,
    #             Variable.in_out == "out",
    #         ),
    #         or_(
    #             Variable.is_pareto.is_(True),
    #             Variable.category.isnot(None)
    #         )
    #     ).all()

    #     if not target_query:
    #         raise exceptions.NotFound("Target data not found")

    #     target_mapping = {item.variable_id: item for item, total_cost in target_query}

    #     paired_data = []
    #     for current_item, total_cost in current_query:
    #         if current_item.variable_id in target_mapping:
    #             paired_data.append(
    #                 (current_item, target_mapping[current_item.variable_id], total_cost)
    #             )

    #     return paired_data

    def get_data_pareto(self, data_id: str, is_uncategorized: bool = False):
        # Subquery for total cost
        total_cost_subq = (
            db.session.query(
                EfficiencyDataDetail.id,
                EfficiencyDataDetail.total_cost()
            )
            .group_by(EfficiencyDataDetail.id)
            .subquery()
        )

        # Base query
        query = (
            db.session.query(EfficiencyDataDetail, total_cost_subq.c.total_cost)
            .join(total_cost_subq, EfficiencyDataDetail.id == total_cost_subq.c.id)
            .join(EfficiencyTransaction)
            .join(Variable)
            .filter(
                Variable.in_out == "out",
                or_(
                    Variable.is_pareto.is_(True),
                    Variable.category.isnot(None)
                )
            )
        )

        query = query.options(selectinload(EfficiencyDataDetail.efficiency_transaction))
        query = query.options(selectinload(EfficiencyDataDetail.variable))
        query = query.options(
            subqueryload(EfficiencyDataDetail.root_causes)
            .subqueryload(EfficiencyDataDetailRootCause.members)
        )

        # raise Exception("here", query)

        # Current data query
        current_query = query.filter(EfficiencyDataDetail.efficiency_transaction_id == data_id)

        # Target data query
        EfficiencyTransactionAlias = aliased(EfficiencyTransaction)
        target_query = (
            query
            .join(EfficiencyTransactionAlias, EfficiencyDataDetail.efficiency_transaction_id == EfficiencyTransactionAlias.id)
            .filter(EfficiencyTransactionAlias.jenis_parameter == "Commision")
        )

        # raise Exception("here", target_query)

        current_results = current_query.all()
        target_results = target_query.all()

        # raise Exception(target_query)

        if not target_results:
            raise exceptions.NotFound("Target data not found")

        # raise Exception("here", current_results)

        # Create mapping for target data
        target_mapping = {item.variable_id: item for item, total_cost in target_results}

        # raise Exception(target_mapping)

        # Pair the data
        paired_data = [
            (current_item, target_mapping[current_item.variable_id], current_total_cost)
            for current_item, current_total_cost in current_results
            if current_item.variable_id in target_mapping
        ]

        # raise Exception(paired_data)

        return paired_data

    def get_data_nphr(self, data_id: str = None, is_target: bool = False, is_kpi: bool = False):
        query = self._query({"variable", "data"})
        nphr_input_name = config.NPHR_VARIABLE_NAME

        if is_target or is_kpi:
            query = query.filter(
                and_(
                    EfficiencyTransaction.jenis_parameter == ("Commision" if is_target else "Niaga"),
                    Variable.excel_variable_name == nphr_input_name,
                )
            )

        else:
            query = query.filter(
                and_(
                    EfficiencyDataDetail.efficiency_transaction_id == data_id,
                    Variable.excel_variable_name == nphr_input_name,
                )
            )

        query = query.options(selectinload(EfficiencyDataDetail.efficiency_transaction))
        query = query.options(selectinload(EfficiencyDataDetail.variable))

        return self._one_or_none(query)

    def get_all_nphr_data(self, data_id: str = None):
        """
        Get current, target, and KPI NPHR data in a single query
        Returns tuple of (current_nphr, target_nphr, kpi_nphr)
        """
        nphr_input_name = config.NPHR_VARIABLE_NAME

        # Create base query with common joins and conditions
        base_query = self.model_class.query.join(EfficiencyDataDetail.variable).join(EfficiencyDataDetail.efficiency_transaction).filter(Variable.excel_variable_name == nphr_input_name)

        # Create case statements to identify each type
        type_case = case(
            (EfficiencyTransaction.jenis_parameter == "current", "current"),
            (EfficiencyTransaction.jenis_parameter == "Commision", "Commision"),
            else_="Niaga"
        ).label("data_type")

        # Combine all conditions in a single query
        combined_query = (
            base_query
            .add_columns(type_case)
            .filter(
                or_(
                    EfficiencyDataDetail.efficiency_transaction_id == data_id,
                    EfficiencyTransaction.jenis_parameter.in_(["Commision", "Niaga"])
                )
            )
        )

        combined_query = combined_query.options(selectinload(EfficiencyDataDetail.efficiency_transaction))
        combined_query = combined_query.options(selectinload(EfficiencyDataDetail.variable))

        # Execute query and process results
        results = combined_query.all()

        # Initialize results
        current_nphr = None
        target_nphr = None
        kpi_nphr = None

        # Map results to their respective variables
        for result, data_type in results:
            if data_type == "current":
                current_nphr = result
            elif data_type == "Commision":
                target_nphr = result
            elif data_type == "Niaga":
                kpi_nphr = result

        return current_nphr, target_nphr, kpi_nphr

    def _join_data(self, query: Select) -> Select:
        return query.join(EfficiencyTransaction)

    def _join_root_cause(self, query: Select) -> Select:
        return query.join(EfficiencyDataDetailRootCause)
