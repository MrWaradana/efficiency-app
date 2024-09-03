""" Defines the Cases repository """

from typing import Optional

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import EfficiencyTransaction
from sqlalchemy import Select
from sqlalchemy.orm.query import Query

from core.repository import BaseRepository


class DataRepository(BaseRepository[EfficiencyTransaction]):

    def get_by_uuid(self, uuid: str, join_: set[str] | None = None):
        query = self._query(join_)
        query = query.filter(EfficiencyTransaction.id == uuid)

        if join_ is not None:
            return self._all_unique(query)

        return self._one_or_none(query)

    def get_query(
        self, start_date, end_date, join_: set[str] | None = None, **kwargs
    ) -> Select:
        # Initialize the query with the EfficiencyTransaction model
        order = {
            "asc": [],  # Order by 'name' and then 'email' ascending
            "desc": ["created_at"],  # Or order by 'created_at' descending
        }

        query = self._query(join_, order_=order)

        # Iterate over the keyword arguments
        for key, value in kwargs.items():
            # If the value is not None or empty
            if value:
                # If the value is a string, filter the query by the attribute of the
                # EfficiencyTransaction model that matches the key with a LIKE query
                if isinstance(value, str):
                    query = query.filter(
                        getattr(EfficiencyTransaction, key).ilike("%{}%".format(value))
                    )
                # If the value is not a string, filter the query by the attribute of the
                # EfficiencyTransaction model that matches the key with an equality query
                else:
                    query = query.filter_by(**{key: value})

        # If both start_date and end_date are provided, filter the query by the periode
        # attribute with a BETWEEN query
        if start_date and end_date:
            query = query.filter(
                EfficiencyTransaction.periode.between(start_date, end_date)
            )
        # If only start_date is provided, filter the query by the periode attribute with a
        # greater than or equal to query
        elif start_date:
            query = query.filter(EfficiencyTransaction.periode >= start_date)
        # If only end_date is provided, filter the query by the periode attribute with a
        # less than or equal to query
        elif end_date:
            query = query.filter(EfficiencyTransaction.periode <= end_date)

        # Return the query object
        return query
