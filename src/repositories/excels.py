""" Defines the Excels repository """

from typing import Optional
from uuid import UUID
from digital_twin_migration.models.efficiency_app import Excel
from sqlalchemy.orm.query import Query


class ExcelsRepository:
    """The repository for the excel model"""

    @staticmethod
    def get_by(**kwargs: dict) -> Query:
        """Query excels by filters

        Args:
            **kwargs (dict): A dictionary of keyword arguments containing the
                column names and their corresponding values to filter the query by.

        Returns:
            Excels: A query object that can be used to retrieve the filtered results.
        """
        return Excel.query.filter_by(**kwargs)

    @staticmethod
    def create(name: str, user_id: UUID, description: str = None, ) -> Excel:
        """Create a new excel

        Args:
            name (str): The name of the excel.
            src (str): The source of the excel.

        Returns:
            Excels: The newly created excel.
        """
        excel = Excel(name, description, user_id)
        return excel.save()

    @staticmethod
    def get_by_id(id: UUID) -> Optional[Excel]:
        """Query a excel by id

        Args:
            id (UUID): The id of the excel to retrieve.

        Returns:
            Excels: The excel with the corresponding id or None if no excel is found.
        """
        return Excel.query.filter_by(id=id).one_or_none()

    @staticmethod
    def delete(id: str) -> None :
        """Delete a specific excel by id

        Args:
            id (UUID): The id of the excel to delete.

        Returns:
            None
        """
        excel = Excel.query.get(id)
        if excel:
            excel.delete()

        return

    @staticmethod
    def update(id: UUID, **columns: dict) -> Excel:
        """Update excel information

        Args:
            id (UUID): The id of the excel to update.
            **columns (dict): A dictionary of keyword arguments containing the column names
                and their corresponding values to update the excel with.

        Returns:
            Excels: The updated excel or None if no excel is found.
        """
        excel = ExcelsRepository.get_by_id(id)

        if excel:
            for key, value in columns.items():
                setattr(excel, key, value)

            excel.commit()

        return excel
