from digital_twin_migration.models.efficiency_app import Case

from .ma import ma

class CaseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Case
        load_instance = True
        include_fk = True
        
