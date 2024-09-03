from functools import reduce
from typing import Any, Generic, Type, TypeVar

from digital_twin_migration.database import Propagation, Transactional, db
from digital_twin_migration.models.abc import BaseModel
from sqlalchemy import Select, func
from sqlalchemy.sql.expression import select

ModelType = TypeVar("ModelType", bound=BaseModel)


class BaseRepository(Generic[ModelType]):
    """Base class for data repositories."""

    def __init__(self, model: Type[ModelType]):
        self.session = db.session
        self.model_class: Type[ModelType] = model

    @Transactional(propagation=Propagation.REQUIRED)
    def create(self, attributes: dict[str, Any] = None) -> ModelType:
        """
        Creates the model instance.

        :param attributes: The attributes to create the model with.
        :return: The created model instance.
        """
        if attributes is None:
            attributes = {}
        model = self.model_class(**attributes)
        self.session.add(model)
        return model

    def create_bulk(self, models: list[ModelType]) -> list[ModelType]:
        self.session.add_all(models)
        return models

    def update(self, model: ModelType, attributes: dict[str, Any] = None) -> ModelType:

        if attributes is None:
            attributes = {}
        for key, value in attributes.items():
            if value is None:
                continue
            setattr(model, key, value)

        return model

    def get_all(
        self, skip: int = 0, limit: int = 100, join_: set[str] | None = None
    ) -> list[ModelType]:
        """
        Returns a list of model instances.

        :param skip: The number of records to skip.
        :param limit: The number of record to return.
        :param join_: The joins to make.
        :return: A list of model instances.
        """
        query = self._query(join_)
        query = query.offset(skip).limit(limit)

        if join_ is not None:
            return self.all_unique(query)

        return self._all(query)

    def get_by(
        self,
        field: str,
        value: Any,
        join_: set[str] | None = None,
        unique: bool = False,
    ) -> ModelType:
        """
        Returns the model instance matching the field and value.

        :param field: The field to match.
        :param value: The value to match.
        :param join_: The joins to make.
        :return: The model instance.
        """
        query = self._query(join_)
        query = self._get_by(query, field, value)

        if join_ is not None:
            return self.all_unique(query)
        if unique:
            return self._one(query)

        return self._all(query)

    def get_by_multiple(
        self,
        join_: set[str] | None = None,
        unique: bool = False,
        attributes: dict[str, Any] = None,
    ):
        if attributes is None:
            attributes = {}

        query = self._query(join_)
        query = self._filter_by(query, **attributes)

        if join_ is not None:
            return self.all_unique(query)
        if unique:
            return self._one(query)

        return self._all(query)

    def delete(self, model: ModelType) -> None:
        """
        Deletes the model.

        :param model: The model to delete.
        :return: None
        """
        self.session.delete(model)

    def _query(
        self,
        join_: set[str] | None = None,
        order_: dict | None = None,
    ) -> Select:
        """
        Returns a callable that can be used to query the model.

        :param join_: The joins to make.
        :param order_: The order of the results. (e.g desc, asc)
        :return: A callable that can be used to query the model.
        """
        query = select(self.model_class)
        query = self._maybe_join(query, join_)
        query = self._maybe_ordered(query, order_)

        return query

    def _all(self, query: Select) -> list[ModelType]:
        """
        Returns all results from the query.

        :param query: The query to execute.
        :return: A list of model instances.
        """
        query = self.session.scalars(query)
        return query.all()

    def _all_unique(self, query: Select) -> list[ModelType]:
        result = self.session.execute(query)
        return result.unique().scalars().all()

    def _first(self, query: Select) -> ModelType | None:
        """
        Returns the first result from the query.

        :param query: The query to execute.
        :return: The first model instance.
        """
        query = self.session.scalars(query)
        return query.first()

    def _filter_by(self, query: Select, **kwargs) -> Select:
        """
        Applies the given keyword arguments as filters to the query.

        :param query: The query to filter.
        :param kwargs: The keyword arguments to filter by.
        :return: The filtered query.
        """
        query = query.filter_by(**kwargs)
        return query

    def _one_or_none(self, query: Select) -> ModelType | None:
        """Returns the first result from the query or None."""
        query = self.session.scalars(query)
        return query.one_or_none()

    def _one(self, query: Select) -> ModelType:
        """
        Returns the first result from the query or raises NoResultFound.

        :param query: The query to execute.
        :return: The first model instance.
        """
        query = self.session.scalars(query)
        return query.one()

    def _count(self, query: Select) -> int:
        """
        Returns the count of the records.

        :param query: The query to execute.
        """
        query = query.subquery()
        query = self.session.scalars(select(func.count()).select_from(query))
        return query.one()

    def _sort_by(
        self,
        query: Select,
        sort_by: str,
        order: str | None = "asc",
        model: Type[ModelType] | None = None,
        case_insensitive: bool = False,
    ) -> Select:
        """
        Returns the query sorted by the given column.

        :param query: The query to sort.
        :param sort_by: The column to sort by.
        :param order: The order to sort by.
        :param model: The model to sort.
        :param case_insensitive: Whether to sort case insensitively.
        :return: The sorted query.
        """
        model = model or self.model_class

        order_column = None

        if case_insensitive:
            order_column = func.lower(getattr(model, sort_by))
        else:
            order_column = getattr(model, sort_by)

        if order == "desc":
            return query.order_by(order_column.desc())

        return query.order_by(order_column.asc())

    def _get_by(self, query: Select, field: str, value: Any) -> Select:
        """
        Returns the query filtered by the given column.

        :param query: The query to filter.
        :param field: The column to filter by.
        :param value: The value to filter by.
        :return: The filtered query.
        """
        return query.where(getattr(self.model_class, field) == value)

    def _maybe_join(self, query: Select, join_: set[str] | None = None) -> Select:
        """
        Returns the query with the given joins.

        :param query: The query to join.
        :param join_: The joins to make.
        :return: The query with the given joins.
        """
        if not join_:
            return query

        if not isinstance(join_, set):
            raise TypeError("join_ must be a set")

        return reduce(self._add_join_to_query, join_, query)

    def _maybe_ordered(self, query: Select, order_: dict | None = None) -> Select:
        """
        Returns the query ordered by the given column.

        :param query: The query to order.
        :param order_: The order to make.
        :return: The query ordered by the given column.
        """
        if order_:
            if order_["asc"]:
                for order in order_["asc"]:
                    query = query.order_by(getattr(self.model_class, order).asc())
            else:
                for order in order_["desc"]:
                    query = query.order_by(getattr(self.model_class, order).desc())

        return query

    def paginate(self, query: Select, page: int, size: int):
        # Calculate total items
        total_items = self._count(query)

        # Calculate total pages
        total_pages = (total_items + size - 1) // size

        # Calculate offset for the current page
        offset = (page - 1) * size

        # Apply limit and offset to the select statemßent
        paginated_stmt = query.offset(offset).limit(size)

        # Execute the paginated query
        items = self._all(paginated_stmt)

        # Create pagination metadata
        pagination = {
            "current_page": page,
            "total_pages": total_pages,
            "page_size": size,
            "total_items": total_items,
            "has_next_page": page < total_pages,
            "has_previous_page": page > 1,
        }

        return pagination, items

    def _add_join_to_query(self, query: Select, join_: set[str]) -> Select:
        """
        Returns the query with the given join.

        :param query: The query to join.
        :param join_: The join to make.
        :return: The query with the given join.
        """
        return getattr(self, "_join_" + join_)(query)
