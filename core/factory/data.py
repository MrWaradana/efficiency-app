

from app.repositories import DataRepository, DataDetailRepository, DataDetailRootCauseRepository
from app.schemas.data import EfficiencyTransactionSchema, EfficiencyDataDetailSchema, EfficiencyDataDetailRootCauseSchema
from digital_twin_migration.models.efficiency_app import EfficiencyTransaction, EfficiencyDataDetail, EfficiencyDataDetailRootCause


class DataFactory():
    def __init__(self, data_repository: DataRepository, data_schema: EfficiencyTransactionSchema) -> None:
        self.data_repository = data_repository
        self.data_schema = data_schema


class DataDetailFactory():
    def __init__(self, data_detail_repository: DataDetailRepository, data_detail_schema: EfficiencyDataDetailSchema) -> None:
        self.data_detail_repository = data_detail_repository
        self.data_detail_schema = data_detail_schema


class DataDetailRootCauseFactory():
    def __init__(self, data_detail_root_cause_repository: DataDetailRootCauseRepository, data_detail_root_cause_schema: EfficiencyDataDetailRootCauseSchema) -> None:
        self.data_detail_root_cause_repository = data_detail_root_cause_repository
        self.data_detail_root_cause_schema = data_detail_root_cause_schema


data_factory = DataFactory(DataRepository(EfficiencyTransaction), EfficiencyTransactionSchema())
data_detail_factory = DataDetailFactory(DataDetailRepository(EfficiencyDataDetail), EfficiencyDataDetailSchema())
data_detail_root_cause_factory = DataDetailRootCauseFactory(DataDetailRootCauseRepository(EfficiencyDataDetailRootCause), EfficiencyDataDetailRootCauseSchema())
