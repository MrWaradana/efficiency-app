from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyDataDetailRootCause, EfficiencyTransaction)
from marshmallow import fields

from app.schemas.variable import VariableSchema as vs
from core.schema import ma


class EfficiencyDataDetailSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EfficiencyDataDetail
        load_instance = True
        include_fk = True

    variable = fields.Nested(vs)


class EfficiencyTransactionSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EfficiencyTransaction
        load_instance = True
        include_fk = True

    efficiency_transaction_details = fields.Nested(
        EfficiencyDataDetailSchema, many=True
    )


class EfficiencyDataDetailRootCauseSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = EfficiencyDataDetailRootCause
        load_instance = True
        include_fk = True
