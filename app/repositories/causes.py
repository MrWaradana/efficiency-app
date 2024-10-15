""" Defines the Cases repository """

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyDataDetailRootCause, VariableCause, VariableCauseAction, Variable)
from sqlalchemy import Select, func, select
from sqlalchemy.orm import aliased, selectinload
from sqlalchemy.orm import contains_eager, joinedload, subqueryload

from core.repository import BaseRepository


class CausesRepository(BaseRepository[VariableCause]):

    def get_by_variable_id(
        self, variable_id: str, join_: set[str] | None = None
    ) -> list[VariableCause]:

        # This code snippet is defining a method `get_by_variable_id` in the `CausesRepository` class.
        # Here's a breakdown of what each step is doing:
        # query = self._query(join_)
        # query = query.filter(VariableCause.variable_id == variable_id)
        # query = query.filter(VariableCause.parent_id == None)

        # if join_ is not None:
        #     return self._all_unique(query)

        # return self._all(query)
        VariableCauseAlias = aliased(VariableCause)
        descendant_subquery = (
            select(VariableCauseAlias.id)
            .filter(VariableCauseAlias.variable_id == variable_id)
            .cte(recursive=True)
        )

        descendant_subquery = descendant_subquery.union_all(
            select(VariableCause.id)
            .join(descendant_subquery, VariableCause.parent_id == descendant_subquery.c.id)
        )

        query = select(VariableCause).filter(
            VariableCause.id.in_(descendant_subquery),
            VariableCause.variable_id == variable_id
        )

        # Use selectinload to eagerly load children
        query = query.options(selectinload(VariableCause.children))
        query = query.options(selectinload(VariableCause.root_cause_members))
        query = query.options(selectinload(VariableCause.actions))
        query = query.options(selectinload(VariableCause.root_causes))

        # Execute the query
        result = self.session.execute(query).scalars().unique().all()

        # Organize results into a tree structure
        tree = [vc for vc in result if vc.parent_id is None]
        
        return tree
    
    def get_count_by_variable_ids(self, variable_ids):
        varc = aliased(VariableCause)
        
        query = (
        self.session.query(
            varc.variable_id.label('variable_id'),
            func.count(varc.id).label('variable_cause_count')
        )
        .filter(varc.variable_id.in_(variable_ids))
        .group_by(varc.variable_id)
    )
        
        return query.all()

    def _join_variable(self, query: Select) -> Select:
        return query.join(VariableCause.variable)

    def _join_children(self, query: Select) -> Select:
        return query.join(VariableCause.children)

    def _join_root_causes(self, query: Select) -> Select:
        return query.join(VariableCause.root_causes)
    
    def _join_root_cause_members(self, query: Select) -> Select:
        return query.join(VariableCause.root_cause_members)

    def _join_actions(self, query: Select) -> Select:
        return query.join(VariableCause.actions)

    def get_by_uuid(self, uuid: str, join_: set[str] | None = None):
        query = self._query(join_)
        query = query.filter(VariableCause.id == uuid)

        if join_ is not None:
            return self._all_unique(query)

        return self._one_or_none(query)
