from digital_twin_migration.models.efficiency_app import EfficiencyTransaction, EfficiencyDataDetail, EfficiencyDataDetailRootCause
from marshmallow import fields
from .ma import ma
    
    

class EfficiencyDataDetailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EfficiencyDataDetail
        load_instance = True
        include_fk = True
        
class EfficiencyTransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EfficiencyTransaction
        load_instance = True
        include_fk = True
        
    