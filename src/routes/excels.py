"""
Defines the blueprint for the excels
"""

from flask import Blueprint
from flask_restful import Api

from resources import ExcelsResource

EXCELS_BLUEPRINT = Blueprint("excels", __name__)

Api(EXCELS_BLUEPRINT).add_resource(ExcelsResource, "/excels")
