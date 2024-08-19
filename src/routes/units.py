"""
Defines the blueprint for the units
"""

from flask import Blueprint
from flask_restful import Api

from resources import UnitsResource

UNITS_BLUEPRINT = Blueprint("units", __name__)

Api(UNITS_BLUEPRINT).add_resource(UnitsResource, "/units")
