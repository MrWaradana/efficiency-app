"""
Define the Case_outputs model
"""

from . import db
from .abc import BaseModel, MetaBaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Case_outputs(db.Model, BaseModel, metaclass=MetaBaseModel):
    """The Case_outputs model"""

    __tablename__ = "case_outputs"

    # ? Default Columns
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    cases_id = db.Column(UUID(as_uuid=True), db.ForeignKey("cases.id"), unique=True)
    variables_id = db.Column(
        UUID(as_uuid=True), db.ForeignKey("variables.id"), unique=True
    )
    data = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())

    # ? Relationships
    cases = db.relationship("Cases", back_populates="case_outputs", lazy=True)
    variables = db.relationship(
        "Variables", back_populates="case_outputs", lazy=True
    )

    def __init__(self, data):
        """Create a new case_outputs"""
        self.data = data
