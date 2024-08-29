""" Defines the Cases repository """

from digital_twin_migration.models.efficiency_app import Case


class CasesRepository:
    """
    The repository for the case model.
    The CasesRepository class provides methods to query the Cases table in the database.
    """

    @staticmethod
    def get_by(**kwargs):
        """
        This static method queries the Cases table in the database based on the provided keyword arguments.
        The method returns a query object that can be used to retrieve the filtered results.

        :param kwargs: A dictionary of keyword arguments containing the column names and their corresponding
                       values to filter the query by.
        :return: A query object that can be used to retrieve the filtered results.
        """

        # Query the Cases table in the database based on the provided filters
        return Case.query.filter_by(**kwargs)

    @staticmethod
    def create(**attributes):
        """
        Create a new case.
        The method creates a new case object based on the provided attributes and adds it to the database.

        :param attributes: A dictionary of keyword arguments containing the attribute names
                           and their corresponding values to create a new Case object with.
        :return: The newly created Case object.
        """
        case = Case(**attributes)
        return case.add()

    @staticmethod
    def get_by_id(id):
        """
        Query a case by id.
        The method returns the case with the corresponding id or None if no case is found.

        :param id: The id of the case to retrieve.
        :type id: int
        :return: The case with the corresponding id or None if no case is found.
        :rtype: Case or None
        """
        return Case.query.filter_by(id=id).one_or_none()

    @staticmethod
    def get_by_name(name):
        """
        Query a case by name.
        The method returns the case with the corresponding name or None if no case is found.

        :param name: The name of the case to retrieve.
        :type name: str
        :return: The case with the corresponding name or None if no case is found.
        :rtype: Case or None
        """
        return Case.query.filter_by(name=name).one_or_none()

    @staticmethod
    def update(id, **columns):
        """
        Update case information.
        The method updates the case with the specified id with the provided columns.

        :param id: The id of the case to update.
        :type id: int
        :param columns: A dictionary of keyword arguments containing the column names
                        and their corresponding values to update the case with.
        :type columns: dict
        :return: The updated Case object or None if no case is found.
        :rtype: Case or None
        """

        case = CasesRepository.get_by_id(id)

        if case:
            for key, value in columns.items():
                setattr(case, key, value)

        return case
