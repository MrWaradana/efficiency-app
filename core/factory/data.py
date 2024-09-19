

from app.repositories import DataRepository, DataDetailRepository, DataDetailRootCauseRepository
from app.schemas.data import EfficiencyTransactionSchema, EfficiencyDataDetailSchema, EfficiencyDataDetailRootCauseSchema
from digital_twin_migration.models.efficiency_app import EfficiencyTransaction, EfficiencyDataDetail, EfficiencyDataDetailRootCause

from core.factory.base import BaseFactory


class DataFactory(BaseFactory):
    def __init__(self, data_repository: DataRepository, data_schema: EfficiencyTransactionSchema) -> None:
        super().__init__(DataRepository, EfficiencyTransactionSchema)
        self.data_repository = data_repository
        self.data_schema = data_schema


class DataDetailFactory(BaseFactory):
    def __init__(self, data_detail_repository: DataDetailRepository, data_detail_schema: EfficiencyDataDetailSchema) -> None:
        super().__init__(DataDetailRepository, EfficiencyDataDetailSchema)
        self.data_detail_repository = data_detail_repository
        self.data_detail_schema = data_detail_schema


class DataDetailRootCauseFactory(BaseFactory):
    def __init__(self, data_detail_root_cause_repository: DataDetailRootCauseRepository, data_detail_root_cause_schema: EfficiencyDataDetailRootCauseSchema) -> None:
        super().__init__(DataDetailRootCauseRepository, EfficiencyDataDetailRootCauseSchema)
        self.data_detail_root_cause_repository = data_detail_root_cause_repository
        self.data_detail_root_cause_schema = data_detail_root_cause_schema


data_factory = DataFactory(DataRepository(EfficiencyTransaction), EfficiencyTransactionSchema())
data_detail_factory = DataDetailFactory(DataDetailRepository(EfficiencyDataDetail), EfficiencyDataDetailSchema())
data_detail_root_cause_factory = DataDetailRootCauseFactory(DataDetailRootCauseRepository(EfficiencyDataDetailRootCause), EfficiencyDataDetailRootCauseSchema())
