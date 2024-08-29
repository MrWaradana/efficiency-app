""" Defines the VariableHeaders repository """

from digital_twin_migration.models.efficiency_app import VariableHeader
from digital_twin_migration.database import Transactional, Propagation

class HeadersRepository:
    """
    The repository for the VariableHeader model.
    The HeadersRepository class provides methods to query the VariableHeaders table in the database.
    """

    @staticmethod
    def get_by(**kwargs):
        """
        This static method queries the VariableHeaders table in the database based on the provided keyword arguments.
        The method returns a query object that can be used to retrieve the filtered results.

        :param kwargs: A dictionary of keyword arguments containing the column names and their corresponding
                       values to filter the query by.
        :return: A query object that can be used to retrieve the filtered results.
        """

        # Query the VariableHeaders table in the database based on the provided filters
        return VariableHeader.query.filter_by(**kwargs)

    @staticmethod
    @Transactional(propagation=Propagation.REQUIRED)
    def create(**attributes):
        """
        Create a new VariableHeader.
        The method creates a new VariableHeader object based on the provided attributes and adds it to the database.

        :param attributes: A dictionary of keyword arguments containing the attribute names
                           and their corresponding values to create a new VariableHeader object with.
        :return: The newly created VariableHeader object.
        """
        header = VariableHeader(**attributes)
        return header.add()

    @staticmethod
    def get_by_id(id):
        """
        Query a VariableHeader by id.
        The method returns the VariableHeader with the corresponding id or None if no VariableHeader is found.

        :param id: The id of the VariableHeader to retrieve.
        :type id: int
        :return: The VariableHeader with the corresponding id or None if no VariableHeader is found.
        :rtype: VariableHeader or None
        """
        return VariableHeader.query.filter_by(id=id).one_or_none()

    @staticmethod
    def update(id, **columns):
        """
        Update VariableHeader information.
        The method updates the VariableHeader with the specified id with the provided columns.

        :param id: The id of the VariableHeader to update.
        :type id: int
        :param columns: A dictionary of keyword arguments containing the column names
                        and their corresponding values to update the VariableHeader with.
        :type columns: dict
        :return: The updated VariableHeader object or None if no VariableHeader is found.
        :rtype: VariableHeader or None
        """

        VariableHeader = HeadersRepository.get_by_id(id)

        if VariableHeader:
            for key, value in columns.items():
                setattr(VariableHeader, key, value)

        return VariableHeader
