from digital_twin_migration.database import Propagation, Transactional, db
from digital_twin_migration.models.efficiency_app import Case


@Transactional(propagation=Propagation.REQUIRED)
def case_seeder():
    # read_excel_value = read_excel_data("./dummy_data/TFELINK.xlsm")
    # excels = read_excel_value
    # print(excels)

    target = Case(name="Target", seq=100)
    kpi = Case(name="KPI Tahunan", seq=200)
    current = Case(name="Current", seq=100)

    db.session.add_all([target, kpi, current])
    db.session.commit()


if __name__ == "__main__":
    case_seeder()
