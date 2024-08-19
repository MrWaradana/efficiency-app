""" Defines the Units repository """

from digital_twin_migration.models import Units


class UnitsRepository:
    """The repository for the unit model"""

    @staticmethod
    def get_by(**kwargs):
        """Query units by filters"""
        return Units.query.filter_by(**kwargs)

    @staticmethod
    def create(unit):
        """Create a new unit"""
        unit = Units(unit)
        return unit.save()

    @staticmethod
    def get_by_id(id):
        """Query a unit by id"""
        return Units.query.filter_by(id=id).one_or_none()

    @staticmethod
    def update(id, **columns):
        """Update unit information"""

        unit = UnitsRepository.get_by_id(id)

        if unit:
            for key, value in columns.items():
                setattr(unit, key, value)

            unit.commit()

        return unit
