"""useless file"""


import pandas as pd
import numpy as np
import pickle as pkl
from dateutil.parser import parse
from datetime import timedelta
from discretization import TemporalDiscretizationn
def packing(filename):
    # Provide info
    
    discretized_file = f"/user_data/discertizated_data/discretizated_{filename}.csv"
    processed_df = pd.read_csv(discretized_file)
    # if Node_f.lower() == 'y': 
    #     print("You should provide list")
        
        flag_dis_t = input('Next we will do the discretization.\nTime discretization is the process of dividing continuous time series data into fixed intervals. For example, convert data per second into data per minute, or daily data into weekly data.\nDo you need time discretization?【y/n】')
        
        if flag_dis_t.lower() == 'y':
            t_dis_method = input('Please choose the method of temporal_discretization.Alternatives is as below: round,ceil,floor.')
            step_tdiscretization = TemporalDiscretizationn.TemporalDiscretizationn(filename = filename, time_format = "%Y-%m-%d %H:%M:%S", time_fitness = time_fitness)
            step_tdiscretization.temporal_discretization(temporal_list)
            step_tdiscretization.save_file()
        
        # Load discretized data
        discretized_file = f"/user_data/discertizated_data/discretizated_{filename}.csv"
        df = pd.read_csv(discretized_file)
        
        # Build node list
        if 'node_id' in node_df.columns:
            node_df = node_df.sort_values(by='node_id')
        node_df.insert(0, 'new_node_id', range(1, len(node_df) + 1))
        node_df.to_csv(f"/user_data/node/{filename}.csv", index=False)
        
        
        
        # Populate ST_raster
        
        
        # Save ST_raster
        np.save(f"/user_data/trafficnode/{filename}.npy", ST_raster)


    elif Grid_f.lower() == 'y' and not Node_f.lower() == 'y':

    elif Node_f.lower() == 'y' and Grid_f.lower() == 'y':

    else:
        raise ValueError("You must choose one!")