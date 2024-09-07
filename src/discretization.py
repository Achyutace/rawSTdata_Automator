"""useless file"""

import pandas as pd
import os
from datetime import datetime,timedelta
import geopandas as gpd
from shapely.geometry import Point, Polygon
import numpy as np
import json
import csv

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

metadata_dir = os.path.join(project_root, 'user_data\\metadata')
preprocessed_data_dir = os.path.join(project_root, 'user_data\\preprocessed_data')
discretizated_data_dir = os.path.join(project_root, 'user_data\\discretizated_data')


class TemporalDiscretizationn():
    def __init__(self,filename,time_format,time_fitness):
        '''
        time_format: the re of time
        listname: which name to process
        '''
        self.json_file_path = os.path.join(metadata_dir, f'column_info_{filename}.json')
        self.preprocessed_file_path = os.path.join(preprocessed_data_dir,f'preprocessed_{filename}.csv')
        self.discretized_file_path = os.path.join(discretizated_data_dir,f'discretizated_{filename}.csv')
        with open(self.preprocessed_file_path,'r') as f:
            self.df = pd.read_csv(f)
        self.time_format = time_format
        self.time_fitness = time_fitness
    # 定义时间离散化函数
    def temporal_discretization_func(self,time_str, method='round'):
        time = datetime.strptime(time_str, self.time_format)
        delta = timedelta(minutes=self.time_fitness)
        
        if method == 'round':
            rounded_time = time - timedelta(minutes=time.minute % self.time_fitness, seconds=time.second)
        elif method == 'ceil':
            rounded_time = time + (delta - timedelta(minutes=time.minute % self.time_fitness, seconds=time.second))
        elif method == 'floor':
            rounded_time = time - timedelta(minutes=time.minute % self.time_fitness, seconds=time.second)
        
        return rounded_time.strftime(self.time_format)
    
    def temporal_discretization(self,list_name,mthd):
        self.df[list_name] = self.df[list_name].apply(lambda x: self.temporal_discretization_func(x, method=mthd))

    # self.df['start_time_discretized'] = self.df['start_time'].apply(lambda x: temporal_discretization_func(x, self.time_fitness, method='round'))
    # self.df['end_time_discretized'] = self.df['end_time'].apply(lambda x: temporal_discretization_func(x, self.time_fitness, method='round'))
    
        
    def save_file(self):
        self.df.to_csv(self.discretized_file_path, index=False)
class spatial_column_discretization():
    def __init__(self,filename,grid_size, grid_type,):
        '''
        grid_size: the size of grid
        '''
        self.json_file_path = os.path.join(metadata_dir, f'column_info_{filename}.json')
        self.preprocessed_file_path = os.path.join(preprocessed_data_dir,f'preprocessed_{filename}.csv')
        self.discretized_file_path = os.path.join(discretizated_data_dir,f'discretizated_{filename}.csv')
        with open(self.discretized_file_path,'r') as f:
            self.df = pd.read_csv(f)
        self.grid_size = grid_size
        self.grid_type = grid_type
    def square_discretization(self):
        # 创建正方形网格
        xmin, ymin, xmax, ymax = self.df.geometry.total_bounds
        x_grid = np.arange(xmin, xmax + self.grid_size, self.grid_size)
        y_grid = np.arange(ymin, ymax + self.grid_size, self.grid_size)
        
        squares = []
        for x in x_grid[:-1]:
            for y in y_grid[:-1]:
                squares.append(Polygon([(x, y), (x + self.grid_size, y), (x + self.grid_size, y + self.grid_size), (x, y + self.grid_size)]))
        
        grid = gpd.GeoDataFrame({'geometry': squares}, crs='EPSG:4326')
        
        # 将数据点分配到网格中
        self.df = gpd.sjoin(self.df, grid, how='left', op='within')
        self.df.drop(columns=['index_right'], inplace=True)
    
    def hexagon_discretization(self):
        # 创建六边形网格
        xmin, ymin, xmax, ymax = self.df.geometry.total_bounds
        x_grid = np.arange(xmin, xmax + self.grid_size, self.grid_size)
        y_grid = np.arange(ymin, ymax + self.grid_size, self.grid_size)
        
        hexagons = []
        for x in x_grid[:-1]:
            for y in y_grid[:-1]:
                hexagon = Polygon([
                    (x + self.grid_size / 2, y),
                    (x + self.grid_size, y + self.grid_size / 2),
                    (x + self.grid_size, y + 3 * self.grid_size / 2),
                    (x + self.grid_size / 2, y + 2 * self.grid_size),
                    (x, y + 3 * self.grid_size / 2),
                    (x, y + self.grid_size / 2)
                ])
                hexagons.append(hexagon)
        
        grid = gpd.GeoDataFrame({'geometry': hexagons}, crs='EPSG:4326')
        
        # 将数据点分配到网格中
        self.df = gpd.sjoin(self.df, grid, how='left', op='within')
        self.df.drop(columns=['index_right'], inplace=True)
    
    def discretize(self):
        if self.grid_type == 'square':
            self.square_discretization()
        elif self.grid_type == 'hexagon':
            self.hexagon_discretization()
        else:
            raise ValueError("Unsupported grid type. Use 'square' or 'hexagon'.")
        
        # 保存离散化后的数据
        self.df.to_csv(self.discretized_file_path, index=False)

    def spatial_discretization(self,x_col_name,y_col_name):
        self.spatial_column_discretization(self.df,x_col_name,y_col_name,grid_size = 1,grid_type = 'quad')
