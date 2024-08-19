"""
Defines the blueprint for the case-inputs
"""

from flask import Blueprint
from flask_restful import Api

from resources import CaseInputsResource

CASE_INPUTS_BLUEPRINT = Blueprint("case-inputs", __name__)

Api(CASE_INPUTS_BLUEPRINT).add_resource(CaseInputsResource, "/case-inputs")
