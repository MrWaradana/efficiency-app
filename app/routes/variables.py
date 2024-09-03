"""
Defines the blueprint for the variables
"""

from flask import Blueprint
from flask_restful import Api

from app.resources import (VariableCauseResource, VariableCausesResource,
                           VariableHeaderResource, VariableHeadersResource,
                           VariableResource, VariablesResource)

VARIABLES_BLUEPRINT = Blueprint("variables", __name__)

Api(VARIABLES_BLUEPRINT).add_resource(VariablesResource, "/variables")
Api(VARIABLES_BLUEPRINT).add_resource(VariableResource, "/variables/<variable_id>")

Api(VARIABLES_BLUEPRINT).add_resource(
    VariableHeadersResource, "/variables/<variable_id>/headers"
)
Api(VARIABLES_BLUEPRINT).add_resource(
    VariableHeaderResource, "/variables/<variable_id>/headers/<header_id>"
)

Api(VARIABLES_BLUEPRINT).add_resource(
    VariableCausesResource, "/variables/<variable_id>/causes"
)
Api(VARIABLES_BLUEPRINT).add_resource(
    VariableCauseResource, "/variables/<variable_id>/causes/<cause_id>"
)
