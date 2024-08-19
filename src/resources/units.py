from flask_restful import Resource
from flask_restful.reqparse import Argument
from utils import parse_params, response
from repositories import UnitsRepository


class UnitsResource(Resource):
    """Units"""

    def get(self):
        """Retrieve all variable"""
        units = UnitsRepository.get_by()

        res = {
            "data": [
                {
                    "id": unit.id,
                    "unit": unit.unit,
                }
                for unit in units
            ]
        }

        return response(res, 200)
