from src import data_preprocess,ST_aligement
import json
import os
import pandas as pd
import shutil
from src.spatial_info_merge import NodeStationInfoBuilding
from src.build_traffic_node import TrafficNodeBuilding
from src.utils.utils import build_uctb_dataset
from dateutil.parser import parse
from datetime import timedelta
filepath = input("Please input the absolute filepath: ")
filename = os.path.splitext(os.path.basename(filepath))[0]
file_extension = os.path.splitext(filepath)[1].lower()
if file_extension != '.csv':
    print(f"The file '{filepath}' is not a CSV file.")
target_dir = './user_data/raw_data'
target_filepath = os.path.join(target_dir, f'{filename}.csv')
shutil.copy(filepath, target_filepath)
print(f"File copied to: {target_filepath}")
# step_one
'''
DataPreprocess
'''
step_one = data_preprocess.DataPreprocess(filename)
# step_one.identify_columns()
with open(step_one.json_file_path,'r')as jf:
    column_info = json.load(jf)
if column_info['temporal_columns'].get("temporal_columns") is None or (column_info['spatial_columns'].get('spatial_id_column') is None and column_info['spatial_columns'].get('geo_spatial_column') is None):
    raise ValueError(f"Something wrong with identify_columns.Please view log.")

step_one.renew_column_name()
step_one.conventional_preprocess()
'''conventional preprocess'''

if column_info['temporal_columns'].get("temporal_columns") is not None:
    step_one.check_temporal_abnormal_values()
if column_info['spatial_columns'].get('geo_spatial_column') is not None:
    step_one.check_lat_lng()
step_one.df_to_csv()
# change the list_name back
temfilepn = f'user_data/preprocessed_data/preprocessed_{filename}.csv'
tempdfpn = pd.read_csv(temfilepn)
print("Now changing list name back...")
oldrow = list(tempdfpn.columns)
for i in range(len(oldrow)):
    for k in column_info['temporal_columns']:
        if k == oldrow[i]:
            oldrow[i] = column_info['temporal_columns'][k]
    for k in column_info['spatial_columns']:
        if k == oldrow[i]:
            oldrow[i] = column_info['spatial_columns'][k]        
tempdfpn.columns = oldrow
tempdfpn.to_csv(temfilepn,index=False)



# step_two 
'''
ST_aligement
'''
flag_s = input("Do you need spatial aligement? Our tools support the interconversion of WGS84, NAD83,GCJ02, CGCS2000.【y/n】")
if flag_s == 'y':
    print('To assist you in transforming data from one coordinate system to another, please follow the steps below to input the details of the two coordinate systems:')
    frms = input('Please enter the name of the original coordinate system: ')
    tos = input('Please enter the name of the target coordinate system: ')
    step_saligement = ST_aligement.dataset_aligement(filename)
    step_saligement.spatial_aligement(frm=frms, to=tos)
flag_t = input("Do you need temporal aligement? 【y/n】")
if flag_t == 'y':
    print('To assist you in temporal discretization, please enter the name of the column you want to discretize:')
    frmt = input('Please enter the column name: ')
    tot = None
    step_taligement = ST_aligement.dataset_aligement(filename)
    step_taligement.temporal_aligement(frm=frmt,to=tot)


# packing
'''
packing to pkl
'''
Node_f = input("Is you are going to build node?【y/n】")
Grid_f = input("Is you are going to build grid?【y/n】")
if Node_f.lower() == 'y' and not Grid_f.lower() == 'y':
    '''input info'''
    print('data_header:')
    print(oldrow)
    try:
        temporal_list = input("Please input temporal_column_name:")
        list_index = input('Please enter the name of the station ID column. If there is none, enter "None":')
        nodelist_input = input('Please enter all the column names related to the traffic node in the format:"col1, col2, ..., colx"(No need to input ""). We will use these to create node_info:')
        nodelist = [x.strip() for x in nodelist_input.split(',')]
        time_range = input('Please enter the time range in the format "YYYY-MM-DD HH:MM:SS,YYYY-MM-DD HH:MM:SS":')
        time_fitness = int(input('Please enter the time fitness in minutes:'))
        '''build node station info'''
        node_info_builder = NodeStationInfoBuilding(filename, nodelist, list_index)
        extracted_df = node_info_builder.extract()
        station_info = node_info_builder.to_dict_list(extracted_df)
        '''build_traffic_node'''
        start_time_str, end_time_str = time_range.split(',')
        start_time = parse(start_time_str)
        end_time = parse(end_time_str) + timedelta(seconds=1)
        node_info_builder = TrafficNodeBuilding(filename, nodelist, time_range, time_fitness, temporal_list, list_index)
        traffic_node = node_info_builder.build_traffic_node()
        build_uctb_dataset(traffic_node=traffic_node, time_fitness=time_fitness, node_station_info=station_info, 
                    start_time = start_time_str,end_time= str(end_time), dataset_name=filename, output_dir= './user_data/processed_data')
    except:
        raise TypeError("?")
    '''packing'''
    
    
