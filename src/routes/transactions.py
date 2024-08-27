"""
Defines the blueprint for the variables
"""

from flask import Blueprint
from flask_restful import Api

from resources import TransactionResource, TransactionsResource, TransactionDataResource, TransactionDataDetailResource

TRANSACTION_BLUEPRIENT = Blueprint("data", __name__)

Api(TRANSACTION_BLUEPRIENT).add_resource(TransactionsResource, "/data")
Api(TRANSACTION_BLUEPRIENT).add_resource(TransactionResource, "/data/<transaction_id>")


Api(TRANSACTION_BLUEPRIENT).add_resource(TransactionDataResource, "/data/<transaction_id>/details")