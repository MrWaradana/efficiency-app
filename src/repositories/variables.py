""" Defines the Variables repository """

from typing import List
from uuid import UUID
from digital_twin_migration.models import Variables, db
from sqlalchemy.orm import joinedload
from sqlalchemy.orm.query import Query


class VariablesRepository:
    """The repository for the variable model"""

    @staticmethod
    def get_by(**kwargs: dict) -> Query:
        """
        Query variables by filters

        Args:
            **kwargs (dict): A dictionary of keyword arguments containing the
                column names and their corresponding values to filter the query by.

        Returns:
            Query: A query object that can be used to retrieve the filtered results.
        """
        return Variables.query.filter_by(**kwargs)

    @staticmethod
    def get_join() -> List[Variables]:
        """
        Query all variables with joined units.

        Returns:
            List[Variables]: A list of variable objects with their respective units.
        """
        return Variables.query.options(joinedload(Variables.units)).all()

    @staticmethod
    def create(
        excels_id: UUID,
        variable: str,
        satuan: str,
        variable_type: str,
        user_id: UUID,
        short_name: str = None,
        category: str = None
    ) -> Variables:
        """Create a new variable

        Args:
            excels_id (UUID): The id of the excel model.
            variable (str): The name of the variable.
            data_location (str): The location of the data.
            units_id (UUID): The id of the units model.
            base_case (str): The base case of the variable.
            variable_type (str): The type of the variable.

        Returns:
            Variables: The newly created variable model.
        """
        variable = Variables(
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
    def get_by_ids(ids: List[str]) -> List[Variables]:
        """Get variables by their ids"""
        return Variables.query.filter(Variables.id.in_(ids)).all()

    @staticmethod
    def bulk_create(variables: List[Variables]):
        """Create a new variable

        Args:
            excels_id (UUID): The id of the excel model.
            variable (str): The name of the variable.
            data_location (str): The location of the data.
            units_id (UUID): The id of the units model.
            base_case (str): The base case of the variable.
            variable_type (str): The type of the variable.

        Returns:
            Variables: The newly created variable model.
        """
        db.session.add_all(variables)
        db.session.flush()
        return

    @staticmethod
    def get_by_id(id):
        """Query a variable by id"""
        return Variables.query.filter_by(id=id).one_or_none()

    @staticmethod
    def update(id, **columns):
        """Update variable information"""

        variable = VariablesRepository.get_by_id(id)

        if variable:
            for key, value in columns.items():
                setattr(variable, key, value)

            variable.commit()

        return variable

    @staticmethod
    def delete(id):
        """Delete variable"""
        variable = VariablesRepository.get_by_id(id)
        if variable:
            variable.delete()
            return True
        return False
