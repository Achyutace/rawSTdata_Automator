import pickle as pkl
import pandas as pd
from utils import utils
import matplotlib.pyplot as plt
import seaborn as sns

import os
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw_data_dir = os.path.join(project_root, 'user_data\\processed_data')
def check_pkl_data(filename, time_fitness):
    pkl_file_path = f'{raw_data_dir}\Bike_DC.pkl'
    with open (pkl_file_path, 'rb') as pf:
        data = pkl.load(pf)


    utils.print_dic_info(data,filename)

    # 3. 数据可视化
    print("\nData Visualization:")
    node = data['Node']['TrafficNode']
    # TODO: df是二维数组，可视化df:
    '''
    任选十列相加，选其中连续的1*7*1440/time_fitness个数据点，绘制可视化图像
    '''
    # 计算需要选择的数据点数量
    num_points = int(1 * 7 * 1440 / time_fitness)
    
    # 任选一列
    col_index = 7  # 这里选择第一列，可以根据需要更改
    selected_col = node[:, col_index]
    
    # 选择连续的数据点
    start_index = 0  # 这里从第一个数据点开始，可以根据需要更改
    selected_data = selected_col[start_index:start_index + num_points]
    
    # 绘制可视化图像
    plt.figure(figsize=(14, 6))
    plt.plot(range(len(selected_data)), selected_data, marker='o')
    plt.title(f'Visualization of Column {col_index} with {num_points} Data Points')
    plt.xlabel('Data Point Index')
    plt.ylabel('Value')
    plt.grid(True)
    plt.show()
    

if __name__ == "__main__":
# 示例调用  
    filename = "Bike_DC"
    check_pkl_data(filename = filename, time_fitness=5)