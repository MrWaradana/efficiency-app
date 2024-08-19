from repositories import ExcelsRepository
from utils.read_excel import read_excel_data


def excels_seeder():
    # read_excel_value = read_excel_data("./dummy_data/TFELINK.xlsm")
    # excels = read_excel_value
    # print(excels)

    excels = [{"name": "TFELINK", "src": "./dummy_data/TFELINK.xlsm"}]

    for e in excels:
        ExcelsRepository.create(e["name"], e["src"])

    print("Excels seeder done!")
