"""
Defines the blueprint for the case-outputs
"""

from flask import Blueprint
from flask_restful import Api

from resources import CaseOutputsResource

CASE_OUTPUTS_BLUEPRINT = Blueprint("case-outputs", __name__)

Api(CASE_OUTPUTS_BLUEPRINT).add_resource(CaseOutputsResource, "/case-outputs")
