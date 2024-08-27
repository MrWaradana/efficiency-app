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
    def create(
        excels_id: UUID,
        variable: str,
        satuan: str,
        variable_type: str,
        user_id: UUID,
        short_name: str = None,
        category: str = None
    ) -> Variable:
        """Create a new variable

        Args:
            excels_id (UUID): The id of the excel model.
            variable (str): The name of the variable.
            data_location (str): The location of the data.
            units_id (UUID): The id of the units model.
            base_case (str): The base case of the variable.
            variable_type (str): The type of the variable.

        Returns:
            Variable: The newly created variable model.
        """
        variable = Variable(
            category=category,
            excels_id=excels_id,
            input_name=variable,
            short_name=short_name,
            satuan=satuan,
            in_out=variable_type,
            created_by=user_id
        )
        return variable.save()
    
    @staticmethod
    def get_by_ids(ids: List[str]) -> List[Variable]:
        """Get variable by their ids"""
        return Variable.query.filter(Variable.id.in_(ids)).all()

    @staticmethod
    def bulk_create(variable: List[Variable]):
        """Create a new variable

        Args:
            excels_id (UUID): The id of the excel model.
            variable (str): The name of the variable.
            data_location (str): The location of the data.
            units_id (UUID): The id of the units model.
            base_case (str): The base case of the variable.
            variable_type (str): The type of the variable.

        Returns:
            Variable: The newly created variable model.
        """
        db.session.add_all(variable)
        db.session.flush()
        return

    @staticmethod
    def get_by_id(id):
        """Query a variable by id"""
        return Variable.query.filter_by(id=id).one_or_none()

    @staticmethod
    def update(id, **columns):
        """Update variable information"""

        variable = VariableRepository.get_by_id(id)

        if variable:
            for key, value in columns.items():
                setattr(variable, key, value)

            variable.commit()

        return variable

    @staticmethod
    def delete(id):
        """Delete variable"""
        variable = VariableRepository.get_by_id(id)
        if variable:
            variable.delete()
            return True
        return False
