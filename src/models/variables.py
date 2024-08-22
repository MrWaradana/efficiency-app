"""
Define the Variables model
"""

from . import db
from enum import Enum
from .abc import BaseModel, MetaBaseModel
from sqlalchemy import Enum as SQLAlchemyEnum
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Variables(db.Model, BaseModel, metaclass=MetaBaseModel):
    """The Variables model"""

    __tablename__ = "variables"

    # ? Default Columns
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    excels_id = db.Column(UUID(as_uuid=True), db.ForeignKey("excels.id"))
    variable = db.Column(db.String(300), nullable=False, unique=True)
    data_location = db.Column(db.String(300), nullable=False, unique=True)
    units_id = db.Column(UUID(as_uuid=True), db.ForeignKey("units.id"))
    base_case = db.Column(db.String(300), nullable=False)
    variable_type = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())

    # ? Relationship
    excels = db.relationship("Excels", back_populates="variables", lazy=True)
    units = db.relationship("Units", back_populates="variables", lazy=True)
    case_inputs = db.relationship("Case_inputs", back_populates="variables", lazy=True)
    case_outputs = db.relationship(
        "Case_outputs", back_populates="variables", lazy=True
    )

    def __init__(
        self, excels_id, variable, data_location, units_id, base_case, variable_type
    ):
        """Create a new Variables""",
        self.excels_id = excels_id
        self.variable = variable
        self.data_location = data_location
        self.units_id = units_id
        self.base_case = base_case
        self.variable_type = variable_type
