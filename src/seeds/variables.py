from repositories import ExcelsRepository, UnitsRepository, VariablesRepository
from utils.read_excel import read_excel_data


def variables_seeder():
    # read_excel_value = read_excel_data("./dummy_data/TFELINK.xlsm")
    # excels = read_excel_value
    # print(excels)
    excels_id = ExcelsRepository.get_by(name="TFELINK")[0].id
    file_path = ExcelsRepository.get_by(name="TFELINK")[0].src
    variables_data = read_excel_data(file_path)

    variables_data = variables_data.iloc[0:, 1:4]

    variables_input = variables_data.loc[7:81]
    variables_output = variables_data.loc[85:]

    # print(variables_input.tail())
    # print(variables_output.head())

    for index, row in variables_input.iterrows():
        units_id = ""
        units = UnitsRepository.get_by().all()
        for unit in units:
            if str(row[2]).lower() == unit.unit.lower():
                units_id = unit.id
            else:
                continue

        VariablesRepository.create(
            excels_id=excels_id,
            variable=row[1],
            data_location=f"B{index+1}",
            units_id=units_id,
            base_case=row[3],
            variable_type="input",
        )

    for index, row in variables_output.iterrows():
        units_id = ""
        units = UnitsRepository.get_by().all()
        for unit in units:
            if str(row[2]).lower() == unit.unit.lower():
                units_id = unit.id
                # print(units_id)
            else:
                continue

        VariablesRepository.create(
            excels_id=excels_id,
            variable=row[1],
            data_location=f"B{index+1}",
            units_id=units_id,
            base_case=row[3],
            variable_type="output",
        )

    print("Variables seeder done!")
