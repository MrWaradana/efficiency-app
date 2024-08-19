from flask_restful import Resource
from flask_restful.reqparse import Argument
from utils import parse_params, response
from repositories import VariablesRepository


class VariablesResource(Resource):
    """Variable resource"""

    # ? excels_id, variable, data_location, units_id, base_case, variable_type
    def get(self):
        """Retrieve all variable"""
        variables = VariablesRepository.get_join()

        res = {
            "data": [
                {
                    "id": variable.id,
                    "excels_id": variable.excels_id,
                    "variable": variable.variable,
                    "data_location": variable.data_location,
                    "units": {
                        "id": variable.units.id,
                        "name": variable.units.unit,
                        # Add any other unit fields you need here
                    },
                    "base_case": variable.base_case,
                    "variable_type": variable.variable_type,
                }
                for variable in variables
            ]
        }

        return response(res, 200)
