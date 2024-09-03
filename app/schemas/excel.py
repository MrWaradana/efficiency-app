from digital_twin_migration.models.efficiency_app import Excel
from marshmallow import fields

from core.schema import ma


class ExcelSchema(ma.SQLAlchemyAutoSchema):
    class Meta:
        model = Excel
        load_instance = True
        include_fk = True
