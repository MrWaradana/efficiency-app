




from flask_restful import Resource

from core.security.jwt_verif import token_required
from app.controllers.data import data_engine_flow_controller
from core.utils import response

class DataEngineFlowResource(Resource):
    
    @token_required
    def get(self, transaction_id):
        data = data_engine_flow_controller.get_all_engine_flow_data(transaction_id)
        
        
        return response(
            200,
            True,
            "Data engine flow retrieved successfully",
            data,
        )