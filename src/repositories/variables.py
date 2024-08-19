""" Defines the Variables repository """

from digital_twin_migration.models import Variables, Units
from sqlalchemy.orm import joinedload


class VariablesRepository:
    """The repository for the variable model"""

    @staticmethod
    def get_by(**kwargs):
        return Variables.query.filter_by(**kwargs)

    @staticmethod
    def get_join():
        return Variables.query.options(joinedload(Variables.units)).all()

    @staticmethod
    def create(excels_id, variable, data_location, units_id, base_case, variable_type):
        """Create a new variable"""
        variable = Variables(
            excels_id, variable, data_location, units_id, base_case, variable_type
        )
        return variable.save()

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
