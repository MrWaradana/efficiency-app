"""
Defines the blueprint for the variables
"""

from flask import Blueprint
from flask_restful import Api
from resources import (TransactionDataDetailResource,
                       TransactionDataDetailsResource,
                       TransactionDataRootCausesResource,
                       TransactionDetailDataParetoResource,
                       TransactionListDataParetoResource, TransactionResource,
                       TransactionsResource)

TRANSACTION_BLUEPRIENT = Blueprint("data", __name__)

Api(TRANSACTION_BLUEPRIENT).add_resource(TransactionsResource, "/data")
Api(TRANSACTION_BLUEPRIENT).add_resource(TransactionResource, "/data/<transaction_id>")


Api(TRANSACTION_BLUEPRIENT).add_resource(
    TransactionDataDetailsResource, "/data/<transaction_id>/details"
)
Api(TRANSACTION_BLUEPRIENT).add_resource(
    TransactionDataDetailResource, "/data/<transaction_id>/details/<detail_id>"
)


Api(TRANSACTION_BLUEPRIENT).add_resource(
    TransactionListDataParetoResource, "/data/<transaction_id>/pareto"
)
Api(TRANSACTION_BLUEPRIENT).add_resource(
    TransactionDetailDataParetoResource, "/data/<transaction_id>/pareto/<detail_id>"
)

Api(TRANSACTION_BLUEPRIENT).add_resource(
    TransactionDataRootCausesResource, "/data/<transaction_id>/root-causes/<detail_id>"
)
