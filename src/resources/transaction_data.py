from datetime import datetime
from flask import request
from flask_restful import Resource
from flask_restful.reqparse import Argument
import requests
from config import WINDOWS_EFFICIENCY_APP_API
from utils import parse_params, response, get_key_by_value
from repositories import VariablesRepository, TransactionRepository
from sqlalchemy.exc import SQLAlchemyError
from digital_twin_migration.models import db, EfficiencyTransactionDetail

from utils.jwt_verif import token_required


class TransactionDataResource(Resource):

    @token_required
    def get(self, user_id, transaction_id):
        """Get all transaction data by transaction id"""

        transaction = TransactionRepository.get_by_id(transaction_id)

        if not transaction:
            return response(404, False, "Transaction not found")

        data = [input.json for input in transaction.efficiency_transaction_details]

        return response(200, True, "Transaction data retrieved successfully", data)
    

class TransactionDataDetailResource(Resource):

    @token_required
    def get(self, user_id, transaction_id, variable_id):
        """Get transaction data by transaction id and variable id"""

        transaction = TransactionRepository.get_by_id(transaction_id)

        if not transaction:
            return response(404, False, "Transaction not found")

        variable = VariablesRepository.get_by_id(variable_id)

        if not variable:
            return response(404, False, "Variable not found")

        data = [input.json for input in transaction.efficiency_transaction_details if input.variable_id == variable_id]

        return response(200, True, "Transaction data retrieved successfully", data)