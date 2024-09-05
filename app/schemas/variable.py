from digital_twin_migration.models.efficiency_app import (
    Variable,
    VariableCause,
    VariableHeader,
)
from marshmallow import fields

from core.schema import ma


class VariableSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Variable
        load_instance = True
        include_fk = True


class VariableHeaderSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VariableHeader
        load_instance = True
        include_fk = True


