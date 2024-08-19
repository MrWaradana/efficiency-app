""" Defines the Excels repository """

from digital_twin_migration.models import Excels


class ExcelsRepository:
    """The repository for the excel model"""

    @staticmethod
    def get_by(**kwargs):
        """Query excels by filters"""
        return Excels.query.filter_by(**kwargs)

    @staticmethod
    def create(name, src):
        """Create a new excel"""
        excel = Excels(name, src)
        return excel.save()

    @staticmethod
    def get_by_id(id):
        """Query a excel by id"""
        return Excels.query.filter_by(id=id).one_or_none()

    @staticmethod
    def update(id, **columns):
        """Update excel information"""

        excel = ExcelsRepository.get_by_id(id)

        if excel:
            for key, value in columns.items():
                setattr(excel, key, value)

            excel.commit()

        return excel
