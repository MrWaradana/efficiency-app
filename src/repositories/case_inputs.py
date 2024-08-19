""" Defines the Case_inputs repository """

# from models import Case_inputs
from digital_twin_migration.models import Case_inputs


class CaseInputsRepository:
    """The repository for the case_input model"""

    @staticmethod
    def get_by(**kwargs):
        """Query case_inputs by filters"""
        return Case_inputs.query.filter_by(**kwargs)

    @staticmethod
    def create(data):
        """Create a new case_input"""
        case_input = Case_inputs(data)
        return case_input.save()

    @staticmethod
    def get_by_id(id):
        """Query a case_input by id"""
        return Case_inputs.query.filter_by(id=id).one_or_none()

    @staticmethod
    def get_by_data(data):
        """Query a case by data"""
        return Case_inputs.query.filter_by(data=data).one_or_none()

    @staticmethod
    def update(id, **columns):
        """Update case_input information"""

        case_input = CaseInputsRepository.get_by_id(id)

        if case_input:
            for key, value in columns.items():
                setattr(case_input, key, value)

            case_input.commit()

        return case_input
