from flask_restful import Resource
from flask_restful.reqparse import Argument
from utils import parse_params, response
from repositories import ExcelsRepository


class ExcelsResource(Resource):
    """Excels"""

    def get(self):
        """Retrieve all variable"""
        excels = ExcelsRepository.get_by().all()

        res = {
            "data": [
                {
                    "id": excel.id,
                    "name": excel.name,
                    "src": excel.src,
                }
                for excel in excels
            ]
        }

        return response(res, 200)
