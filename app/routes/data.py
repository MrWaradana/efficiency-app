"""
Defines the blueprint for the variables
"""

from flask import Blueprint
from flask_restful import Api

from app.resources import (DataDetailListResource, DataDetailResource,
                           DataListResource, DataResource, DataListParetoResource)

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
# Api(TRANSACTION_BLUEPRIENT).add_resource(
#     TransactionDetailDataParetoResource, "/data/<transaction_id>/pareto/<detail_id>"
# )

# Api(TRANSACTION_BLUEPRIENT).add_resource(
#     TransactionDataRootCausesResource, "/data/<transaction_id>/root-causes/<detail_id>"
# )
