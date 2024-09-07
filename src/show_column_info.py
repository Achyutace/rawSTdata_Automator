"""useless file"""

import pandas as pd
import os
import json

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw_data_dir = os.path.join(project_root, 'user_data\\raw_data')
metadata_dir = os.path.join(project_root, 'user_data\\metadata')
def show_column_information(filename):
# Read the CSV file
    csv_file_path = os.path.join(raw_data_dir,f'{filename}.csv')
    json_file_path = os.path.join(metadata_dir, f'column_info_{filename}.json')
    with open(json_file_path,'r') as jf:
        column_info = json.load(jf)
    df = pd.read_csv(csv_file_path)

    # Print basic information about the DataFrame
    print("Basic information about the DataFrame:")
    print(df.info())

    # Print the first few rows of the DataFrame
    print("\nFirst few rows of the DataFrame:")
    print(df.head())

    # Print basic statistical information about the temporal columns
    print("\nBasic statistical information about the temporal columns:")
    print(df[column_info['spatial_columns']].describe())

    # Print basic statistical information about the spatial columns
    print("\nBasic statistical information about the spatial columns:")
    print(df[column_info['temporal_columns']].describe())

    # Print basic statistical information about the dropped columns
    print("\nBasic statistical information about the dropped columns:")
    dropped_columns = column_info['dropped_columns']

if __name__ == "__main__":
    show_column_information('Bike_DC')