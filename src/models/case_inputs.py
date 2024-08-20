"""
Define the Case_inputs model
"""

from . import db
from .abc import BaseModel, MetaBaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Case_inputs(db.Model, BaseModel, metaclass=MetaBaseModel):
    """The Case_inputs model"""

    __tablename__ = "case_inputs"

    # ? Default Columns
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cases_id = db.Column(UUID(as_uuid=True), db.ForeignKey("cases.id"))
    variables_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("variables.id")
    )
    data = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())

    # ? Relationships
    cases = db.relationship("Cases", back_populates="case_inputs", lazy=True)
    variables = db.relationship("Variables", back_populates="case_inputs", lazy=True)

    def __init__(self, cases_id, variables_id, data):
        """Create a new case_inputs"""
        self.cases_id = cases_id
        self.variables_id = variables_id
        self.data = data
