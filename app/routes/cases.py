"""
Defines the blueprint for the cases
"""

from flask import Blueprint
from flask_restful import Api

from app.resources import CaseResource, CasesResource

CASES_BLUEPRINT = Blueprint("cases", __name__)

Api(CASES_BLUEPRINT).add_resource(CasesResource, "/cases")
Api(CASES_BLUEPRINT).add_resource(CaseResource, "/cases/<case_id>")
