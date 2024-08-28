""" Defines the Variable repository """

from typing import List
from uuid import UUID
from digital_twin_migration.models.efficiency_app import Variable
from digital_twin_migration.models import db
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.query import Query


class VariablesRepository:
    """The repository for the variable model"""

    @staticmethod
    def get_by(**kwargs: dict) -> Query:
        """
        Query variable by filters

        Args:
            **kwargs (dict): A dictionary of keyword arguments containing the
                column names and their corresponding values to filter the query by.

        Returns:
            Query: A query object that can be used to retrieve the filtered results.
        """
        return Variable.query.filter_by(**kwargs)

    @staticmethod
    def get_join() -> List[Variable]:
        """
        Query all variable with joined units.

        Returns:
            List[Variable]: A list of variable objects with their respective units.
        """
        return Variable.query.options(joinedload(Variable.units)).all()

    @staticmethod
    def create(**attributes) -> Variable:
        """Create a new variable

        Parameters:
            attributes (dict): A dictionary of keyword arguments containing the attribute names
                and their corresponding values to create a new Variable object with.

        Returns:
            Variable: The newly created variable model.
        """
        new_variable = Variable(**attributes)
        return new_variable.add()
    
    @staticmethod
    def get_by_ids(ids: List[str]) -> List[Variable]:
        """Get variable by their ids

        Args:
            ids (List[str]): The list of id of the variable.

        Returns:
            List[Variable]: A list of variable object.
        """
        return Variable.query.filter(Variable.id.in_(ids)).all()

    @staticmethod
    def bulk_create(variable: List[Variable]):
        """Create a new variable

        Args:
            variable (List[Variable]): The list of variable object to create.

        Returns:
            None
        """
        db.session.add_all(variable)
        db.session.flush()
        return

    @staticmethod
    def get_by_id(id):
        """Query a variable by id

        Args:
            id (str): The id of the variable.

        Returns:
            Variable or None: The variable object if found, None otherwise.
        """
        return Variable.query.filter_by(id=id).one_or_none()

    @staticmethod
    def update(id, **columns):
        """Update variable information

        Args:
            id (str): The id of the variable.
            **columns (dict): The dictionary of column names and their corresponding values.

        Returns:
            Variable or None: The updated variable object if found, None otherwise.
        """

        variable = VariablesRepository.get_by_id(id)

        if variable:
            for key, value in columns.items():
                setattr(variable, key, value)

        return variable

    @staticmethod
    def delete(id):
        """Delete variable

        Args:
            id (str): The id of the variable.

        Returns:
            bool: True if the variable is deleted, False otherwise.
        """
        variable = VariablesRepository.get_by_id(id)
        if variable:
            variable.delete()
            return True
        return False
