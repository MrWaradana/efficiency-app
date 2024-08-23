"""
Defines the blueprint for the variables
"""

from flask import Blueprint
from flask_restful import Api

from resources import TransactionResource, TransactionsResource

TRANSACTION_BLUEPRIENT = Blueprint("transactions", __name__)

Api(TRANSACTION_BLUEPRIENT).add_resource(TransactionsResource, "/transactions")
Api(TRANSACTION_BLUEPRIENT).add_resource(TransactionResource, "/transactions/<transaction_id>")
