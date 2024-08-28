from collections import defaultdict
from datetime import datetime
from flask import request
from flask_restful import Resource
from flask_restful.reqparse import Argument
import requests
from sqlalchemy import and_
from utils import parse_params, response, get_key_by_value, calculate_gap, calculate_nilai_losses
from repositories import VariablesRepository, TransactionRepository
from sqlalchemy.exc import SQLAlchemyError
from digital_twin_migration.models import db
from digital_twin_migration.models.efficiency_app import EfficiencyDataDetail, EfficiencyTransaction, Variable

from utils.jwt_verif import token_required


class TransactionDataDetailsResource(Resource):

    @token_required
    @parse_params(
        Argument("type", location="args", required=False, default="in"),
    )
    def get(self, user_id, transaction_id, type):
        """Get all transaction data by transaction id"""

        data_details = EfficiencyDataDetail.query.join(EfficiencyDataDetail.efficiency_transaction).join(EfficiencyDataDetail.variable).filter(
            and_(
                EfficiencyTransaction.id == transaction_id,
                Variable.in_out == type
            )
        ).all()

        data = [detail.json for detail in data_details]

        return response(200, True, "Data details retrieved successfully", data)


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

        print(data[0])

        raise Exception(data[0])

        return response(200, True, "Transaction data retrieved successfully", data)


class TransactionDataParetoResource(Resource):

    @token_required
    def get(self, user_id, transaction_id):
        current_data = EfficiencyDataDetail.query.join(EfficiencyDataDetail.efficiency_transaction).join(EfficiencyDataDetail.variable).filter(
            and_(
                EfficiencyTransaction.id == transaction_id,
                Variable.in_out == "out"
            )
        ).all()

        target_data = EfficiencyDataDetail.query.join(EfficiencyDataDetail.efficiency_transaction).join(EfficiencyDataDetail.variable).filter(
            and_(
                EfficiencyTransaction.jenis_parameter == "Target",
                Variable.in_out == "out"
            )
        ).all()

        current_dict = {item.variable_id: item for item in current_data}
        target_dict = {item.variable_id: item for item in target_data}

        calculated_data = []
        aggregated_nilai_losses = defaultdict(float)

        for variable_id, current_item in current_dict.items():
            target_item = target_dict.get(variable_id)
            if target_item:
                gap = calculate_gap(target_item.nilai, current_item.nilai)

                if gap is None:
                    raise Exception(gap, target_item.nilai_string, current_item.nilai)
                
                nilai_losses = calculate_nilai_losses(
                    gap, current_item.deviasi, current_item.persen_hr)

                aggregated_nilai_losses[current_item.variable.category] += nilai_losses if nilai_losses is not None else 0

                calculated_data.append({
                    'id': current_item.id,
                    'variable': current_item.variable.json,
                    'existing_data': current_item.nilai,
                    'reference_data': target_item.nilai,
                    'deviasi': current_item.deviasi,
                    'persen_hr': current_item.persen_hr,
                    'nilai_losses': nilai_losses,
                    'gap': gap
                })

        data = []
        for category, losses in aggregated_nilai_losses.items():
            category_data = {
                'category': category,
                'total_losses': losses,
                'data': [item for item in calculated_data if item['variable']['category'] == category]

            }

            data.append(category_data)
        
        data_sorted = sorted(data, key=lambda x: x['total_losses'], reverse=True)

        return response(200, True, "Data retrieved successfully", data_sorted)
