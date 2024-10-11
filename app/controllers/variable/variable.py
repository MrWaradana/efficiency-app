

import requests
from app.repositories.variables import VariablesRepository
from core.controller.base import BaseController
from digital_twin_migration.models.efficiency_app import Variable
from core.factory import variable_factory
from core.utils import response
from app.controllers.excels import excel_repository
import aiohttp
import asyncio
from werkzeug import exceptions
from worker import fetch_variable_data
from core.utils.formula import PIFormula


variable_repository = variable_factory.variable_repository
variable_schema = variable_factory.variable_schema


class VariableController(BaseController[Variable]):
    def __init__(self, variable_repository: VariablesRepository = variable_repository):
        super().__init__(model=Variable, repository=variable_repository)
        self.variable_repository = variable_repository

    def get(self, id):
        return self.model.get(id)

    def get_all(self, excel_id, type):

        is_connected_to_pi = False

        username = 'tjb.piwebapi'
        password = 'PLNJepara@2024'

        try:
            res = requests.get(f"https://10.47.0.54/piwebapi", auth=(username, password) , timeout=2, verify=False)

            if res.ok:
                is_connected_to_pi = True

        except requests.exceptions.RequestException:
            is_connected_to_pi = False

        excel = excel_repository.get_by_uuid(excel_id)

        if not excel:
            print(f"Excel {excel_id} not found")
            raise exceptions.NotFound(f"Excel {excel_id} not found")

        variables = variable_repository.get_by_multiple(
            attributes={"excel_id": excel_id, "in_out": type}
        )

        variables_base_case = []
        task_results = []
        pi_formula = PIFormula(variables)

        for variable in variables:
            base_case = variable.konstanta if variable.konstanta is not None else "N/A"

            if not variable.konstanta and is_connected_to_pi and variable.web_id and variable.web_id != "Not used" and variable.web_id != "Konstanta":
                url = F"https://10.47.0.54/piwebapi/streams/{variable.web_id}/value"
                # Submit task to Celery
                task = fetch_variable_data.delay(url, username, password)
                task_results.append((task, variable))  # Store the task along with the variable
            else:
                variables_base_case.append({**variable_schema.dump(variable), "base_case": base_case})

        # Wait for Celery tasks to complete
        for task, variable in task_results:
            base_case = task.get()  # This will block until the task is finished

            # Check if variable have formula
            if variable.formula:
                try:
                    # Dynamically get the formula function from pi_formula
                    formula_function = getattr(pi_formula, variable.formula)

                    # Check if it's callable and apply the formula to base_case
                    if callable(formula_function):
                        base_case = formula_function(base_case)
                    else:
                        # Log a warning if formula is not a valid function
                        print(f"Warning: {variable.formula} is not callable.")

                except AttributeError:
                    # Handle case where formula does not exist in pi_formula
                    print(f"Error: {variable.formula} is not found in pi_formula.")
                    raise exceptions.InternalServerError(f"Error: {variable.formula} is not found in pi_formula.")

            variables_base_case.append({**variable_schema.dump(variable), "base_case": base_case})

        return variables_base_case

    def create(self, data):
        return self.model.create(data)

    def update(self, id, data):
        return self.model.update(id, data)

    def delete(self, id):
        return self.model.delete(id)


variable_controller = VariableController()
