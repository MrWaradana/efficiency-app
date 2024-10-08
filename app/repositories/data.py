""" Defines the Cases repository """

from datetime import date, datetime
from typing import Optional

from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyTransaction, Variable, ThermoflowStatus)
from sqlalchemy import Select, and_, func
from sqlalchemy.orm import contains_eager, joinedload, subqueryload
from sqlalchemy.orm.query import Query
from sqlalchemy.orm import aliased
from core.repository import BaseRepository


class DataRepository(BaseRepository[EfficiencyTransaction]):

    def get_by_uuid(self, uuid: str, join_: set[str] | None = None):
        query = self._query(join_)
        query = query.filter(EfficiencyTransaction.id == uuid)

        if join_ is not None:
            return self._all_unique(query)

        return self._one_or_none(query)

    def get_newest_data(self):
        query = self.model_class.query
        query = query.order_by(EfficiencyTransaction.created_at.desc())
        return query.first()

    def get_daily_increment(self):
        today = date.today()

        # Get the highest daily increment for today
        max_increment = (
            self.session.query(func.max(EfficiencyTransaction.sequence))
            .filter(func.date(EfficiencyTransaction.created_at) == today)
            .scalar()
        )

        if max_increment is None:
            return 1
        else:
            return max_increment + 1

    def get_by_unique_id(self, unique_id):
        return self.model_class.query.filter_by(unique_id=unique_id).first()

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

    def get_data_trending(self, start_date: str, end_date: str, variable_ids: list):

        if isinstance(start_date, str):
            start_date = datetime.fromisoformat(
                start_date
            )  # Convert from ISO string to datetime
        if isinstance(end_date, str):
            end_date = datetime.fromisoformat(
                end_date
            )  # Convert from ISO string to datetime

        query = (
            self.session.query(EfficiencyTransaction)
            .join(EfficiencyTransaction.efficiency_transaction_details)
            .filter(
                and_(
                    EfficiencyTransaction.periode.between(start_date, end_date),
                    EfficiencyDataDetail.variable_id.in_(variable_ids)
                )
            )
            .options(
                contains_eager(EfficiencyTransaction.efficiency_transaction_details)
            ).order_by(EfficiencyTransaction.periode.asc())
        )

        return query.all()

    def get_target_data_by_variable(self, variable_ids, type=None, is_unique=False):

        query = (
            self.session.query(EfficiencyTransaction)
            .join(EfficiencyTransaction.efficiency_transaction_details)
            .filter(
                and_(
                    EfficiencyDataDetail.variable_id.in_(variable_ids),
                    EfficiencyTransaction.jenis_parameter == "target"
                )
            )
            .options(
                contains_eager(EfficiencyTransaction.efficiency_transaction_details)
            )
        )

        return query.first() if is_unique else query.all()

    def update_thermoflow_status(self, status: bool):
        thermoflow_status = ThermoflowStatus.query.first()
        thermoflow_status.is_running = status
        db.session.commit()

    def get_performance_chart_data(self, variable_ids: list):

        # query = self.session.query(EfficiencyTransaction).options(
        #     contains_eager(EfficiencyTransaction.efficiency_transaction_details)
        # ).join(EfficiencyTransaction.efficiency_transaction_details).filter(EfficiencyDataDetail.variable_id.in_(variable_ids))

        # one = query.where(EfficiencyTransaction.performance_test_weight == 50).all()
        # two = query.where(EfficiencyTransaction.performance_test_weight == 60).all()
        # three = query.where(EfficiencyTransaction.performance_test_weight == 70).all()
        # four = query.where(EfficiencyTransaction.performance_test_weight == 80).all()

        # return query.all()

        # Create an alias for the joined table to use in the contains_eager
        # First, get the latest transaction IDs for each test weight
# This code snippet is performing a query to retrieve the latest transaction IDs for each unique
# `performance_test_weight` value in the `EfficiencyTransaction` table. It then uses these IDs to
# fetch all the details for these transactions, specifically for the `variable_ids` provided.
        latest_transaction_subquery = (
            self.session.query(
                EfficiencyTransaction.id,
                EfficiencyTransaction.performance_test_weight
            )
            .filter(EfficiencyTransaction.performance_test_weight < 100)
            .distinct(EfficiencyTransaction.performance_test_weight)
            .order_by(
                EfficiencyTransaction.performance_test_weight,
                EfficiencyTransaction.created_at.desc()
            )
            .subquery()
        )

        # Then use these IDs to get all the details for these transactions
        efficiency_details = aliased(EfficiencyDataDetail)

        query = (
            self.session.query(EfficiencyTransaction)
            .join(latest_transaction_subquery,
                EfficiencyTransaction.id == latest_transaction_subquery.c.id)
            .join(
                efficiency_details,
                and_(
                    EfficiencyTransaction.id == efficiency_details.efficiency_transaction_id,
                    efficiency_details.variable_id.in_(variable_ids)
                )
            )
            .options(
                contains_eager(
                    EfficiencyTransaction.efficiency_transaction_details,
                    alias=efficiency_details
                )
            )
        ).all()

        return query

    def _join_data_details(self, query: Select) -> Select:
        return query.join(EfficiencyDataDetail)
