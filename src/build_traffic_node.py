"""
Module for building traffic node information.
"""

from spatial_info_merge import NodeStationInfoBuilding
import pandas as pd
from dateutil.parser import parse
from datetime import timedelta
import numpy as np
from tqdm import tqdm

class TrafficNodeBuilding(NodeStationInfoBuilding):
    """
    Class to build traffic node information.
    """
    def __init__(self, filename, nodelist, time_range, time_fitness, temporal_list, list_index=None):
        super().__init__(filename, nodelist, list_index)
        self.time_range = time_range
        self.time_fitness = time_fitness
        self.num_nodes = None
        self.temporal_list = temporal_list

    def add_node_id(self):
        """
        Add node ID to the DataFrame.
        """
        tempdf = super().extract()
        self.num_nodes = len(tempdf)
        df = pd.read_csv(self.filepath)
        try:
            index_mapping = dict(zip(tempdf[self.list_index], tempdf['ind']))
            df['new_id'] = df[self.list_index].map(index_mapping)
        except Exception as exc:
            raise TypeError("An error which never be seen") from exc
        return df

    def build_traffic_node(self):
        """
        Build traffic node information.
        """
        df = self.add_node_id()
        start_time_str, end_time_str = self.time_range.split(',')
        start_time = parse(start_time_str)
        end_time = parse(end_time_str) + timedelta(seconds=1)
        total_minutes = int((end_time - start_time).total_seconds() / 60)
        time_intervals = total_minutes // self.time_fitness
        st_raster = np.zeros((time_intervals, self.num_nodes))
        for _, row in tqdm(df.iterrows(), total=df.shape[0], desc="Processing rows"):
            time_index = int((parse(row[self.temporal_list]) - start_time).total_seconds() / 60 // self.time_fitness)
            node_id = row["new_id"]
            if 0 <= time_index < time_intervals:
                st_raster[time_index, node_id] += 1
            else:
                raise TypeError(f"Warning: time_index {time_index} is out of bounds. Please check start_time and end_time input!")
        return st_raster

class TrafficGridBuilding:
    """
    Class to build traffic grid information.
    """
    def __init__(self):
        pass

if __name__ == "__main__":
    TEST = 1
    if TEST == 1:
        FILENAME = 'Bike_DC'
        NODELIST = ['start_station_id', 'start_station_name', 'start_lng', 'start_lat']
        LIST_INDEX = 'start_station_id'
        TIME_RANGE = "2024-05-01 00:00:00,2024-05-31 23:59:59"
        TIME_FITNESS = 5
        TEMPORAL_LIST = "started_at"
        node_info_builder = TrafficNodeBuilding(FILENAME, NODELIST, TIME_RANGE, TIME_FITNESS, TEMPORAL_LIST, LIST_INDEX)
        extracted_npy = node_info_builder.build_traffic_node()
        np.save('./data/temp/test_node.npy', extracted_npy)
    elif TEST == 2:
        pass