
from app.repositories import VariablesRepository
from app.schemas.variable import VariableSchema


class VariabelFactory():
    def __init__(self, variable_repository: VariablesRepository, variable_schema:VariableSchema) -> None:
        self.variable_repository = variable_repository
        self.variable_schema = variable_schema
        
        