"""
Defines the blueprint for the excels
"""

from flask import Blueprint
from flask_restful import Api

from resources import ExcelsResource, ExcelResource

EXCELS_BLUEPRINT = Blueprint("excels", __name__)

Api(EXCELS_BLUEPRINT).add_resource(ExcelsResource, "/excels")
Api(EXCELS_BLUEPRINT).add_resource(ExcelResource, "/excels/<excel_id>")

