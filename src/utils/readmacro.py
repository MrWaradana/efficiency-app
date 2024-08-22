# -*- coding: utf-8 -*-
"""
Created on Tue Aug  6 19:43:49 2024

@author: User
"""

import os
import win32com.client

def run_macro(file_path, macro_name):
    # Ensure the file path is absolute
    file_path = os.path.abspath(file_path)
    
    # Check if the file exists
    if not os.path.isfile(file_path):
        print(f"File not found: {file_path}")
        return
    
    # Initialize Excel application
    excel = win32com.client.Dispatch("Excel.Application")
    excel.Visible = True  # Set to True if you want to see the Excel window

    # Open the workbook
    wb = excel.Workbooks.Open(file_path)

    try:
        # Run the macro
        excel.Application.Run(f"'{wb.Name}'!{macro_name}")
        print(f"Macro {macro_name} executed successfully.")
    except Exception as e:
        print(f"Error running macro {macro_name}: {e}")
    finally:
        pass
        # Close the workbook without saving
        #wb.Close(SaveChanges=False)
        # Quit Excel application
        #excel.Quit()

# Example usage
file_path = 'tes.xlsm'  # Use the correct path to your file
macro_name = 'Macro1'  # Replace with the name of your macro
run_macro(file_path, macro_name)