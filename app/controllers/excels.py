
from app.repositories.excels import ExcelsRepository
from app.schemas.excel import ExcelSchema
from core.cache.cache_manager import Cache
from core.controller import BaseController
from digital_twin_migration.database import Propagation, Transactional
from digital_twin_migration.models.efficiency_app import Excel


excel_schema = ExcelSchema()
excel_repository = ExcelsRepository(Excel)


class ExcelController(BaseController[Excel]):
    def __init__(self, excel_repository: ExcelsRepository = excel_repository):
        super().__init__(model=Excel, repository=excel_repository)
        self.excel_repository = excel_repository

    @Cache.cached("get_all_excel")
    def get_all_excel(self):
        excels = self.excel_repository.get_all()

        return excels

    @Transactional(propagation=Propagation.REQUIRED)
    def create_excel(self, name, user_id):
        excel = excel_repository.create({"excel_filename": name, "created_by": user_id})

        return excel

    def get_excel(self, excel_id):
        excel = excel_repository.get_by_uuid(excel_id)

        if not excel:
            return False

        return excel

    @Transactional(propagation=Propagation.REQUIRED)
    def delete_excel(self, excel):
        excel_repository.delete(excel)

    @Transactional(propagation=Propagation.REQUIRED)
    def update_excel(self, excel, name):
        excel_repository.update(excel, {"excel_filename": name})


excel_controller = ExcelController()
