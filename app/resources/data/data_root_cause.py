from collections import defaultdict

from digital_twin_migration.database import Propagation, Transactional, db
from digital_twin_migration.models.efficiency_app import (
    EfficiencyDataDetail, EfficiencyDataDetailRootCause, EfficiencyTransaction,
    Variable, VariableCause)
from flask_restful import Resource
from flask_restful.reqparse import Argument
from schemas import EfficiencyDataDetailSchema, VariableSchema
from sqlalchemy import and_, func
from utils import calculate_gap, calculate_nilai_losses, parse_params, response
from utils.jwt_verif import token_required

variable_schema = VariableSchema()
data_details_schema = EfficiencyDataDetailSchema()


class TransactionDataRootCausesResource(Resource):
    @token_required
    def get(self, user_id, transaction_id, detail_id):
        variable_id = EfficiencyDataDetail.query.get(detail_id).variable_id

        root_causes = VariableCause.query.filter(
            and_(
                # EfficiencyDataDetailRootCause.data_detail_id == detail_id,
                VariableCause.variable_id == variable_id,
                VariableCause.parent_id.is_(None),
            )
        ).all()

        raise Exception(root_causes)

        return response(
            200,
            True,
            "Data root causes retrieved successfully",
            data_details_schema.dump(data_root_causes, many=True),
        )
