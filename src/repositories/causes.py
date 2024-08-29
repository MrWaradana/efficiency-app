""" Defines the Cases repository """

from digital_twin_migration.models.efficiency_app import VariableCause
from digital_twin_migration.database import Transactional, Propagation

class CausesRepository:
    """
    The repository for the case model
    """

    
    @staticmethod
    def get_by(**kwargs):
        """
        Query cases by filters

        Args:
            **kwargs (dict): A dictionary of keyword arguments containing the
                column names and their corresponding values to filter the query by.

        Returns:
            Query: A query object that can be used to retrieve the filtered results.
        """
        return VariableCause.query.filter_by(**kwargs)

    @Transactional(propagation=Propagation.REQUIRED)
    @staticmethod
    def create(**attributes):
        """
        Create a new Cause

        Args:
            **attributes (dict): A dictionary of keyword arguments containing the attribute names
                and their corresponding values to create a new Cause object with.

        Returns:
            VariableCause: The newly created Cause.
        """
        case = VariableCause(**attributes)
        return case.add()

    @staticmethod
    def update(id, **columns):
        """
        Update case information

        Args:
            id (int): The id of the case to update.
            **columns (dict): A dictionary of keyword arguments containing the column names
                and their corresponding values to update the case with.

        Returns:
            VariableCause or None: The updated Case object or None if no case is found.
        """

        case = CausesRepository.get_by_id(id)

        if case:
            for key, value in columns.items():
                setattr(case, key, value)

        return case
