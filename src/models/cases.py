"""
Define the Cases model
"""

from . import db
from .abc import BaseModel, MetaBaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Cases(db.Model, BaseModel, metaclass=MetaBaseModel):
    """The Cases model"""

    __tablename__ = "cases"

    # ? Column Defaults
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(300), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())

    # ? Relationship
    case_inputs = db.relationship("Case_inputs", back_populates="cases", lazy=True)
    case_outputs = db.relationship(
        "Case_outputs", back_populates="cases", lazy=True
    )

    def __init__(self, name):
        """Create a new Cases"""
        self.name = name
