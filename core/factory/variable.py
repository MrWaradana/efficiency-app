
from app.repositories import VariablesRepository, HeadersRepository, CausesRepository
from app.schemas import VariableSchema, VariableHeaderSchema, VariableCauseSchema
from core.factory.base import BaseFactory

from digital_twin_migration.models.efficiency_app import Variable, VariableCause, VariableHeader

class VariableFactory(BaseFactory):
    def __init__(self, variable_repository: VariablesRepository, variable_schema: VariableSchema) -> None:
        super().__init__(VariablesRepository, VariableSchema)
        self.variable_repository = variable_repository
        self.variable_schema = variable_schema


class VariableHeaderFactory(BaseFactory):
    def __init__(self, variable_header_repository: VariablesRepository, variable_header_schema: VariableSchema) -> None:
        super().__init__(HeadersRepository, VariableHeaderSchema)
        self.variable_header_repository = variable_header_repository
        self.variable_header_schema = variable_header_schema


class VariableCauseFactory(BaseFactory):
    def __init__(self, variable_cause_repository: VariablesRepository, variable_cause_schema: VariableSchema) -> None:
        super().__init__(CausesRepository, VariableCauseSchema)
        self.variable_cause_repository = variable_cause_repository
        self.variable_cause_schema = variable_cause_schema
        
        
variable_factory = VariableFactory(VariablesRepository(Variable), VariableSchema())
variable_header_factory = VariableHeaderFactory(HeadersRepository(VariableHeader), VariableHeaderSchema())
variable_cause_factory = VariableCauseFactory(CausesRepository(VariableCause), VariableCauseSchema())