"""
Defines the blueprint for the variables
"""

from flask import Blueprint
from flask_restful import Api

from resources import (
    TransactionResource,
    TransactionsResource,
    TransactionDataDetailsResource,
    TransactionDataParetoResource,
)

TRANSACTION_BLUEPRIENT = Blueprint("data", __name__)

Api(TRANSACTION_BLUEPRIENT).add_resource(TransactionsResource, "/data")
Api(TRANSACTION_BLUEPRIENT).add_resource(TransactionResource, "/data/<transaction_id>")


Api(TRANSACTION_BLUEPRIENT).add_resource(
    TransactionDataDetailsResource, "/data/<transaction_id>/details"
)

Api(TRANSACTION_BLUEPRIENT).add_resource(
    TransactionDataParetoResource, "/data/<transaction_id>/pareto"
)
