"""
Define the Units model
"""

from . import db
from .abc import BaseModel, MetaBaseModel
from sqlalchemy.dialects.postgresql import UUID
import uuid


class Units(db.Model, BaseModel, metaclass=MetaBaseModel):
    """The Units model"""

    __tablename__ = "units"

    # ? Column Defaults
    id = db.Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    # abbreviation = db.Column(db.String(300), nullable=False)
    unit = db.Column(db.String(300), unique=True)
    created_at = db.Column(db.DateTime, nullable=False, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, nullable=True, server_default=db.func.now())

    # ? Relationships
    variables = db.relationship("Variables", back_populates="units", lazy=True)

    def __init__(self, unit):
        """Create a new units"""
        # self.abbreviation = abbreviation
        self.unit = unit
