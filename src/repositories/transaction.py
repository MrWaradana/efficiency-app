""" Defines the Cases repository """

from datetime import date
from typing import Optional
from uuid import UUID
from digital_twin_migration.models.efficiency_app import EfficiencyTransaction
from digital_twin_migration.models import db
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
    def get_query(start_date, end_date, **kwargs):
        """
        Get a query for EfficiencyTransaction.

        This function generates a query for the EfficiencyTransaction model based on the
        provided start_date, end_date, and keyword arguments. The function is used to
        retrieve filtered results from the EfficiencyTransaction table in the database.

        Args:
            start_date (date): The start date of the query. If provided, the query will
                only return transactions with a periode greater than or equal to the
                start_date.
            end_date (date): The end date of the query. If provided, the query will only
                return transactions with a periode less than or equal to the end_date.
            **kwargs: The keyword arguments to filter the query by. The function will
                iterate over the keyword arguments and filter the query based on each
                key-value pair.

        Returns:
            Query: The query object to retrieve filtered results.
        """
        # Initialize the query with the EfficiencyTransaction model
        res = EfficiencyTransaction.query

        # Iterate over the keyword arguments
        for key, value in kwargs.items():
            # If the value is not None or empty
            if value:
                # If the value is a string, filter the query by the attribute of the
                # EfficiencyTransaction model that matches the key with a LIKE query
                if isinstance(value, str):
                    res = res.filter(getattr(EfficiencyTransaction,
                                     key).ilike("%{}%".format(value)))
                # If the value is not a string, filter the query by the attribute of the
                # EfficiencyTransaction model that matches the key with an equality query
                else:
                    res = res.filter_by(**{key: value})

        # If both start_date and end_date are provided, filter the query by the periode
        # attribute with a BETWEEN query
        if start_date and end_date:
            res = res.filter(EfficiencyTransaction.periode.between(start_date, end_date))
        # If only start_date is provided, filter the query by the periode attribute with a
        # greater than or equal to query
        elif start_date:
            res = res.filter(EfficiencyTransaction.periode >= start_date)
        # If only end_date is provided, filter the query by the periode attribute with a
        # less than or equal to query
        elif end_date:
            res = res.filter(EfficiencyTransaction.periode <= end_date)

        # Order the query by the created_at attribute in descending order
        res = res.order_by(EfficiencyTransaction.created_at.desc())

        # Return the query object
        return res

    @staticmethod
    def create(**attributes) -> EfficiencyTransaction:
        """
        This static method is used to create a new EfficiencyTransaction in the database.

        Parameters:
            attributes (dict): A dictionary of keyword arguments containing the attribute names
                and their corresponding values to create a new EfficiencyTransaction object with.

        Returns:
            EfficiencyTransaction: The newly created EfficiencyTransaction object.
        """

        # Create a new EfficiencyTransaction object using the provided attributes.
        # The attributes are passed as keyword arguments to the constructor of the EfficiencyTransaction class.
        # This allows the EfficiencyTransaction class to initialize its attributes with the provided values.
        # The keyword arguments are expected to match the names of the attributes defined in the EfficiencyTransaction class.
        new_transaction = EfficiencyTransaction(**attributes)

        # The newly created EfficiencyTransaction object is added to the database using the add() method.
        # The add() method is called on the new_transaction object, which is an instance of the EfficiencyTransaction class.
        # The add() method is responsible for adding the object to the database session and committing the changes to the database.
        # It returns the newly created EfficiencyTransaction object.
        # The returned EfficiencyTransaction object is then returned by the create() method.
        return new_transaction.add()

    @staticmethod
    def bulk_create(models: list):
        """
        This static method is used to bulk create new EfficiencyTransaction objects in the database.

        Parameters:
            models (list): A list of EfficiencyTransaction objects to create.

        Returns:
            None: This function does not return anything since it is used to create new objects in the database.
        """

        # Add all the models to the session
        # The models are added to the database session using the add_all() method.
        # This method takes a list of objects as input and adds them to the session.
        # The objects in the list are expected to be instances of the EfficiencyTransaction class.
        db.session.add_all(models)

        # Flush the session to execute the INSERT statements for all the models
        # The session is flushed using the flush() method.
        # The flush() method is called on the session object.
        # Flushing the session causes the session to execute any pending database operations,
        # including executing any pending INSERT statements for the objects in the session.
        db.session.flush()

        # Return None to indicate that no EfficiencyTransaction object is being returned
        # This function does not return any EfficiencyTransaction object since it is used to create new objects in the database.
        # Instead, it returns None to indicate that the function has completed its task of creating new objects in the database.
        return

    @staticmethod
    def get_by_id(id: str) -> Optional[EfficiencyTransaction]:
        """
        This static method queries the EfficiencyTransaction table in the database
        based on the provided id.

        Parameters:
            id (str): The id of the EfficiencyTransaction object to retrieve.

        Returns:
            Optional[EfficiencyTransaction]: The EfficiencyTransaction object with the
            corresponding id, or None if no object is found.

        Description of the code:
            - The get_by_id() method is a static method that belongs to the TransactionRepository class.
            - This method is responsible for querying the EfficiencyTransaction table in the database
              based on the provided id.
            - The method takes a single parameter, id, which is a string representing the id of the
              EfficiencyTransaction object to retrieve.
            - The method returns an Optional object that contains the EfficiencyTransaction object
              with the corresponding id, or None if no object is found.
            - The EfficiencyTransaction table is queried using the query.filter_by() method.
            - The query.filter_by() method takes a keyword argument, id=id, which specifies the
              column name (id) and its corresponding value (the provided id).
            - The query.filter_by() method returns a query object that can be used to retrieve
              the filtered results from the database.
            - The query object is then passed to the one_or_none() method.
            - The one_or_none() method is called on the query object to retrieve a single result
              from the database. If no result is found, None is returned. If a result is found,
              the EfficiencyTransaction object is returned.
        """
        return EfficiencyTransaction.query.filter_by(id=id).one_or_none()

    @staticmethod
    def get_by_name(name: str) -> Optional[EfficiencyTransaction]:
        """
        This static method queries the EfficiencyTransaction table in the database
        based on the provided name.

        Parameters:
            name (str): The name of the EfficiencyTransaction object to retrieve.

        Returns:
            Optional[EfficiencyTransaction]: The EfficiencyTransaction object with the
            corresponding name, or None if no object is found.

        Description of the code:
            - The get_by_name() method is a static method that belongs to the TransactionRepository class.
            - This method is responsible for querying the EfficiencyTransaction table in the database
              based on the provided name.
            - The method takes a single parameter, name, which is a string representing the name of the
              EfficiencyTransaction object to retrieve.
            - The method returns an Optional object that contains the EfficiencyTransaction object
              with the corresponding name, or None if no object is found.
            - The EfficiencyTransaction table is queried using the query.filter_by() method.
            - The query.filter_by() method takes a keyword argument, name=name, which specifies the
              column name (name) and its corresponding value (the provided name).
            - The query.filter_by() method returns a query object that can be used to retrieve
              the filtered results from the database.
            - The query object is then passed to the one_or_none() method.
            - The one_or_none() method is called on the query object to retrieve a single result
              from the database. If no result is found, None is returned. If a result is found,
              the EfficiencyTransaction object is returned.
        """
        return EfficiencyTransaction.query.filter_by(name=name).one_or_none()

    @staticmethod
    def update(id: str, **columns: dict) -> Optional[EfficiencyTransaction]:
        """
        Update case information

        This method updates the case with the specified id with the provided columns.

        Parameters:
            id (str): The id of the case to update.
            **columns (dict): A dictionary of keyword arguments containing the column names
                and their corresponding values to update the case with.

        Returns:
            Optional[EfficiencyTransaction]: The updated EfficiencyTransaction object or None if no case is found.

        Description of the code:
            - The update() method is a static method that belongs to the TransactionRepository class.
            - This method is responsible for updating a case in the database with the provided columns.
            - The method takes two parameters: id, which is a string representing the id of the case to update,
              and **columns, which is a dictionary of keyword arguments containing the column names
              and their corresponding values to update the case with.
            - The method returns an Optional object that contains the updated EfficiencyTransaction object
              or None if no case is found.
            - The method first retrieves the case to update using the get_by_id() method.
            - If a case is found, it iterates over each key-value pair in the **columns dictionary.
            - For each key-value pair, it sets the corresponding attribute of the case object to the new value.
            - The setattr() function is used to dynamically set the attribute of the case object.
            - After updating the case, the method returns the updated case object.
        """

        case = TransactionRepository.get_by_id(id)

        if case:
            for key, value in columns.items():
                setattr(case, key, value)

        return case

    