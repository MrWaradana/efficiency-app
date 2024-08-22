"""
Define the Excels model
"""

from . import db
from .abc import BaseModel, MetaBaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Excels(db.Model, BaseModel, metaclass=MetaBaseModel):
    """The Excels model"""

    __tablename__ = "excels"

    # ? Column Defaults
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = db.Column(db.String(300), nullable=False, unique=True)
    src = db.Column(db.String(300), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())

    # ? Relationships
    variables = db.relationship("Variables", back_populates="excels", lazy=True)

    def __init__(self, name, src):
        """Create a new Excels"""
        self.name = name
        self.src = src
