from repositories import ExcelsRepository, UnitsRepository
from utils.read_excel import read_excel_data


def units_seeder():
    # read_excel_value = read_excel_data("./dummy_data/TFELINK.xlsm")
    # excels = read_excel_value
    # print(excels)
    file_path = ExcelsRepository.get_by(name="TFELINK")[0].src
    excel_data = read_excel_data(file_path)

    units_data = excel_data.iloc[0:, 2].unique()

    for u in units_data:
        UnitsRepository.create(u)

    print("Units seeder done!")
