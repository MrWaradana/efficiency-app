import pandas as pd


def read_excel_data(file_path):
    # Load the Excel file
    df = pd.read_excel(file_path, sheet_name=0, engine="openpyxl", header=None)

    # Slice the dataframe to start from B8
    data = df.iloc[7:,]  # 7th row (index 7) and 2nd column (index 1) for B8

    # Generate cell references like B8, B9, etc.
    # data_locations = [f'B{i+8}' for i in range(len(data))]

    # print(data)

    return data


# read_excel_data("./dummy_data/TFELINK.xlsm")
