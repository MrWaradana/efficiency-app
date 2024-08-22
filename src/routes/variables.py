"""
Defines the blueprint for the variables
"""

from flask import Blueprint
from flask_restful import Api

from resources import VariablesResource

VARIABLES_BLUEPRINT = Blueprint("variables", __name__)

Api(VARIABLES_BLUEPRINT).add_resource(VariablesResource, "/variables")
