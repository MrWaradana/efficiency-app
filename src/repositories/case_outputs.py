""" Defines the Case_outputs repository """

from digital_twin_migration.models import Case_outputs


class CaseOutputsRepository:
    """The repository for the case_output model"""

    @staticmethod
    def get_by(**kwargs):
        """Query case_outputs by filters"""
        return Case_outputs.query.filter_by(**kwargs)

    @staticmethod
    def create(data):
        """Create a new case_output"""
        case_output = Case_outputs(data)
        return case_output.save()

    @staticmethod
    def get_by_id(id):
        """Query a case_output by id"""
        return Case_outputs.query.filter_by(id=id).one_or_none()

    @staticmethod
    def get_by_data(data):
        """Query a case by data"""
        return Case_outputs.query.filter_by(data=data).one_or_none()

    @staticmethod
    def update(id, **columns):
        """Update case_output information"""

        case_output = CaseOutputsRepository.get_by_id(id)

        if case_output:
            for key, value in columns.items():
                setattr(case_output, key, value)

            case_output.commit()

        return case_output
