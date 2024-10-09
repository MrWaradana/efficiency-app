from digital_twin_migration.models.efficiency_app import VariableCause, VariableCauseAction
from marshmallow import fields

from app.schemas.data import EfficiencyDataDetailRootCauseMemberSchema as root
from core.schema import ma


class VariableCauseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VariableCause
        load_instance = True
        include_fk = True


    children = fields.Nested(lambda: VariableCauseSchema, many=True)
    root_cause_members = fields.Nested(root, many=True)
    actions = fields.Nested(lambda: VariableCauseActionSchema, many=True)
    
class VaribleCauseSchemaJustChildren(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VariableCause
        load_instance = True
        include_fk = True

    children = fields.Nested(lambda: VariableCauseSchema, many=True, exclude=("root_cause_members", "actions"))


class VariableCauseActionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VariableCauseAction
        load_instance = True
        include_fk = True
