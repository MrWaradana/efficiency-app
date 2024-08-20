""" Defines the Cases repository """

from digital_twin_migration.models import Cases


class CasesRepository:
    """The repository for the case model"""

    @staticmethod
    def get_by(**kwargs):
        """Query cases by filters"""
        return Cases.query.filter_by(**kwargs)

    @staticmethod
    def create():
        """Create a new case"""
        case_count = Cases.query.count()
        new_case_name = f"Case {case_count + 1}"
        case = Cases(new_case_name)
        return case.add()

    @staticmethod
    def get_by_id(id):
        """Query a case by id"""
        return Cases.query.filter_by(id=id).one_or_none()

    @staticmethod
    def get_by_name(name):
        """Query a case by name"""
        return Cases.query.filter_by(name=name).one_or_none()

    @staticmethod
    def update(id, **columns):
        """Update case information"""

        case = CasesRepository.get_by_id(id)

        if case:
            for key, value in columns.items():
                setattr(case, key, value)

            case.commit()

        return case
