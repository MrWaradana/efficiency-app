from marshmallow import fields

from app.schemas.data import EfficiencyDataDetailRootCauseSchema as root
from core.schema import ma

from digital_twin_migration.models.efficiency_app import (
    VariableCause,

)


class VariableCauseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = VariableCause
        load_instance = True
        include_fk = True

    children = fields.Nested(lambda: VariableCauseSchema, many=True)
    root_causes = fields.Nested(root, many=True)
