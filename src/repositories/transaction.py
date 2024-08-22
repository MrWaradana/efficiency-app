""" Defines the Cases repository """

from typing import Optional
from uuid import UUID
from digital_twin_migration.models import EfficiencyTransaction, db
from sqlalchemy.orm.query import Query


class TransactionRepository:
    """The repository for the case model"""

    @staticmethod
    def get_by(**kwargs: dict) -> Query:
        """
        This static method queries the EfficiencyTransaction table in the database
        based on the provided keyword arguments.

        :param kwargs: A dictionary of keyword arguments containing the column names
                       and their corresponding values to filter the query by.
        :return: A query object that can be used to retrieve the filtered results.
        """
        # Query the EfficiencyTransaction table in the database based on the provided filters
        return EfficiencyTransaction.query.filter_by(**kwargs)

    @staticmethod
    def create(
        periode: str,
        jenis_parameter: str,
        excel_id: str,
        variable_id: str,
        nilai: float,
        created_by: str,
    ) -> EfficiencyTransaction:
        """
        Create a new case

        :param periode: The periode of the case (str)
        :param jenis_parameter: The jenis parameter of the case (str)
        :param excel_id: The excel id of the case (UUID)
        :param variable_id: The variable id of the case (UUID)
        :param nilai: The nilai of the case (float)
        :param created_by: The user who created the case (UUID)
        :return: The newly created case (EfficiencyTransaction)
        """
        inputs = EfficiencyTransaction(
            periode=periode,
            jenis_parameter=jenis_parameter,
            excel_id=excel_id,
            variable_id=variable_id,
            nilai=nilai,
            created_by=created_by,
        )
        return inputs.save()

    @staticmethod
    def bulk_create(inputs: list[EfficiencyTransaction]):
        db.session.add_all(inputs)
        db.session.flush()
        return

    @staticmethod
    def get_by_id(id: str) -> Optional[EfficiencyTransaction]:
        """Query a case by id"""
        return EfficiencyTransaction.query.filter_by(id=id).one_or_none()

    @staticmethod
    def get_by_name(name: str) -> Optional[EfficiencyTransaction]:
        """Query a case by name"""
        return EfficiencyTransaction.query.filter_by(name=name).one_or_none()

    @staticmethod
    def update(id: str, **columns: dict) -> Optional[EfficiencyTransaction]:
        """Update case information"""

        case = TransactionRepository.get_by_id(id)

        if case:
            for key, value in columns.items():
                setattr(case, key, value)

            case.commit()

        return case
