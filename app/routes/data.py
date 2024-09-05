"""
Defines the blueprint for the variables
"""

from flask import Blueprint
from flask_restful import Api

from app.resources import (
    DataDetailListResource,
    DataDetailResource,
    DataListParetoResource,
    DataListResource,
    DataResource,
    DataRootCausesListResource,
)

TRANSACTION_BLUEPRIENT = Blueprint("data", __name__)

Api(TRANSACTION_BLUEPRIENT).add_resource(DataListResource, "/data")
Api(TRANSACTION_BLUEPRIENT).add_resource(DataResource, "/data/<transaction_id>")


Api(TRANSACTION_BLUEPRIENT).add_resource(
    DataDetailListResource, "/data/<transaction_id>/details"
)
Api(TRANSACTION_BLUEPRIENT).add_resource(
    DataDetailResource, "/data/<transaction_id>/details/<detail_id>"
)


Api(TRANSACTION_BLUEPRIENT).add_resource(
    DataListParetoResource, "/data/<transaction_id>/pareto"
)

Api(TRANSACTION_BLUEPRIENT).add_resource(
    DataRootCausesListResource, "/data/<transaction_id>/root/<detail_id>"
)
