from digital_twin_migration.models.efficiency_app import EfficiencyTransaction, EfficiencyDataDetail, EfficiencyDataDetailRootCause

from .ma import ma

class EfficiencyTransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EfficiencyTransaction
        load_instance = True
        include_fk = True
        
