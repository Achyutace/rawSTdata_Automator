import pandas as pd
import json
import os
import openai
import csv
from .utils import utils
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
raw_data_dir = os.path.join(project_root, 'user_data\\raw_data')
metadata_dir = os.path.join(project_root, 'user_data\\metadata')
preprocessed_data_dir = os.path.join(project_root, 'user_data\\preprocessed_data')
openai.api_key = 'sk-c36b06173d7048b6873dcc901a85e341'
openai.api_base = "https://api.deepseek.com"
dbg = True


"""
preprocess raw data
"""
class DataPreprocess():
    """
    
    """

    def __init__(self,filename):
        self.filename = filename
        self.csv_file_path = os.path.join(raw_data_dir,f'{filename}.csv')
        self.json_file_path = os.path.join(metadata_dir, f'column_info_{filename}.json')
        self.preprocessed_file_path = os.path.join(preprocessed_data_dir,f'preprocessed_{filename}.csv')
        self.df = None
    def identify_columns(self):
        '''
        step1
        '''
        
        column_info = {
        'temporal_columns': {
            'temporal_columns': ['list name of temporal_columns'],
            'start_time': 'list name,if you are not sure, write None',
            'end_time': 'list name,if you are not sure, write None'
        },
        'spatial_columns': {
            'geo_spatial_column': 'list name,if you are not sure, write None',
            'pickup_longitude': 'list name,if you are not sure, write None',
            'dropoff_longitude': 'list name,if you are not sure, write None',
            'pickup_latitude': 'list name,if you are not sure, write None',
            'dropoff_latitude': 'list name,if you are not sure, write None',
            'pickup_sitename': 'list name,if you are not sure, write None',
            'dropout_sitename': 'list name,if you are not sure, write None',
            'pickup_site_id': 'list name,if you are not sure, write None',
            'dropout_site_id': 'list name,if you are not sure, write None',
        },
        'time_fitness': 'time fitness,if you are not sure, write None',
        'dropped_columns': 'you should put your extracted information here'
    }
        json_template = str(column_info)
        csv_example_prompt = 'The example data shows below.column_names contain\''
        try:
            print('In identification...')
            with open(self.csv_file_path,'r')as csvf:
                csvreader = csv.reader(csvf)
                i=0
                for i, row in enumerate(csvreader):
                    if i >= 5:
                        break
                    csv_example_prompt+=f'{row}'
                    if i==0:
                        print('raw data header: ',row)
                        csv_example_prompt+='Please mainly refer to dataset_description and make sure that startdate format and enddate format match the example data.'
                    response = openai.ChatCompletion.create(
                model='deepseek-chat',
                messages=[{'role':'system',"content":'I want you to act as a data scientist. You are going to extract information to fill in the value of json template provided by users from descriptions of dataset. If you are not sure about meaning of the keys, you can ask me for help. Besides, you must add your reason for each extracted information. You can set value to null if you are not sure about the extracted information. Caution! you only need to output a json file.'},
                        {'role':'user',"content":'Hello!'},
                        {'role':'assistant',"content":'Please provide json template contains keys.'},
                {'role':'user',"content":json_template+'You should be truthful and provide the correct information. You can set value to None if you are not sure about the extracted information.'},
                {'role':'assistant',"content":'Oh I see. Can you tell me what does GeospatialColumn in the json template means?'},
                {'role':'user',"content":'It means columns relevant to spatial information in the dataset. For example, latitude,longitude... You can set value to None if you are not sure about the extracted information.You can choose more than one.'},
                {'role':'assistant',"content":'What does temporal_columns in the json template means?'},
                {'role':'user',"content":'It means all the column belongs to temporal datas.'},
                {'role':'assistant',"content":'What does dropped_column in the json template means?'},
                {'role':'user',"content":'It means the column that was not mentioned in the spacial or temporal column above.It always not None.'},
                {'role':'assistant',"content":'Sure. So can you provide me with the detailed dataset description?'},
                {'role':'user',"content":'Sure. Followings are dataset_description.\n'+csv_example_prompt+'\nPlease directly output the extracted json file. Caution! You must find strong evidence to support your extraction of TimeFitness information. Otherwise, you just put \'null\' to the corresponding place. Now you can output the extracted json file.',}],
                
            )
            response_content = response.choices[0].message.content
            try:
                discretization_information = json.loads(response_content)
            except:
                discretization_information = list(utils.extract_json_objects(response_content))[0]
            
            
            if discretization_information['spatial_columns']['geo_spatial_column'] is not None:
                city_info = {
                    'spatial_info':{
                        'city_name':None,
                        'max_lat':None,
                        'max_lng':None,
                        'min_lat':None,
                        'min_lng':None,
                    }
                }
                city_template = str(city_info)
                city = input("which city is the dataset from:")
                city_response = openai.ChatCompletion.create(
                model='deepseek-chat',
                messages=[
                {'role':'user',"content":'Hello!'},
                {'role':'assistant',"content":'Which city info do you want to know?'},
                {'role':'user',"content":f'I want to know json like this:{city_template} of {city}.Please directly output the extracted json file.'},
                ],
            )
            city_response_content = city_response.choices[0].message.content
            try:
                city_discretization_information = json.loads(city_response_content)
            except:
                city_discretization_information = list(utils.extract_json_objects(city_response_content))[0]
            discretization_information.update(city_discretization_information)
            with open(self.json_file_path, 'w') as json_file:
                json.dump(discretization_information, json_file, indent=4)
        except:
            raise TypeError('FILE CANNOT BE FOUND! Please check ./user_data/raw_data.')
        
    def renew_column_name(self):
        print('Normalizing column names for data...')
        with open(self.csv_file_path, 'r',newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
            datas = list(reader)
        with open(self.json_file_path,'rb') as jf:
            column_info = json.load(jf)
            for j in column_info:
                try:
                    for k in column_info[j]:
                        try:
                            for ind,l in enumerate(header):
                                try:
                                    if column_info[j][k] == l:
                                        if dbg == True:
                                            print(f"Changed column name '{header[ind]}' to '{k}'")
                                        header[ind] = k
                                except:
                                    pass
                            
                        except:
                            raise TypeError("column_info_key is not match with header")
                except:
                    pass
        #print(header)
        with open(self.csv_file_path,'w', newline='') as file_two:
            writer = csv.writer(file_two)
            writer.writerow(header)
            writer.writerows(datas)
    
    def extract_columns(self):
        self.df = pd.read_csv(self.csv_file_path)
        with open(self.csv_file_path, 'r',newline='') as csvfile:
            reader = csv.reader(csvfile)
            header = next(reader)
        with open(self.json_file_path,'rb') as jf:
            column_info = json.load(jf)
        '''
        droppedList = []
        for key in header:
            for j in column_info['dropped_columns']:
                if(j==key):
                    droppedList.append(key)
        if droppedList == []:
            raise ValueError("Nothing Dropped!Please check data/metadata/column_info_filename.json!")
        else:
            print('The deleted lists is as follows: ',droppedList)
            for key in droppedList:
                self.df.drop(key, axis=1, inplace=True)
        '''
    def conventional_preprocess(self):
        self.df = pd.read_csv(self.csv_file_path)
        print('Data preprocessing...')
        df = self.df
        print('preprocessed data header: ',df.head())
        # 检查数据的基本信息
        print("Dataframe Info:")
        print(df.info())

        # 检查缺失值
        print("\nMissing Values:")
        print(df.isnull().sum())

        # 处理缺失值，这里我们选择删除含有缺失值的行
        df.dropna(inplace=True)

        # 检查重复值
        print("\nDuplicate Rows:")
        print(df.duplicated().sum())

        # 处理重复值，这里我们选择删除重复的行
        df.drop_duplicates(inplace=True)

        self.df = df
    def check_lat_lng(self):
        df = self.df
        with open(self.json_file_path,'r') as jf:
            column_info = json.load(jf)
        # 检查经纬度范围是否合理（例如，经度范围-180到180，纬度范围-90到90）
        invalid_coordinates = df[
            (df['pickup_longitude'] < -180) | (df['pickup_longitude'] > 180) |
            (df['pickup_latitude'] < -90) | (df['pickup_latitude'] > 90) |
            (df['dropoff_longitude'] < -180) | (df['dropoff_longitude'] > 180) |
            (df['dropoff_latitude'] < -90) | (df['dropoff_latitude'] > 90)
        ]
        print("\nInvalid Coordinates:")
        print(invalid_coordinates)
        # 处理异常经纬度，这里我们选择删除这些行
        df = df[
            (df['pickup_latitude'] >= column_info['spatial_info']['min_lat']) & (df['pickup_latitude'] <= column_info['spatial_info']['max_lat']) &
            (df['pickup_longitude'] >= column_info['spatial_info']['min_lng']) & (df['pickup_longitude'] <= column_info['spatial_info']['max_lng']) &
            (df['dropoff_latitude'] >= column_info['spatial_info']['min_lat']) & (df['dropoff_latitude'] <= column_info['spatial_info']['max_lat']) &
            (df['dropoff_longitude'] >= column_info['spatial_info']['min_lng']) & (df['dropoff_longitude'] <= column_info['spatial_info']['max_lng'])
        ]
        self.df = df

    def check_spatial_abnormal_values(self,x_row_name,y_row_name,max_x=None,min_x=None,max_y=None,min_y=None):
        df = self.df
        df = df[
            (df[f'{x_row_name}'] >= min_x) & (df[f'{x_row_name}'] <= max_x) &
            (df[f'{y_row_name}'] >= min_y) & (df[f'{y_row_name}'] <= max_y)
        ]
        self.df = df

    def check_temporal_abnormal_values(self):
        # 检查日期时间是否有异常值（例如，dropoff时间早于pickup时间）
        # 确保日期时间格式正确
        df = self.df
        df['start_time'] = pd.to_datetime(df['start_time'])
        df['end_time'] = pd.to_datetime(df['end_time'])
        invalid_dates = df[df['end_time'] < df['start_time']]
        print("\nInvalid Dates (dropoff before pickup):")
        print(invalid_dates)

        # 处理异常日期时间，这里我们选择删除这些行
        df = df[df['end_time'] >= df['start_time']]
        self.df = df
    def df_to_csv(self):
        self.df.to_csv(self.preprocessed_file_path,index=False)
    
def main():
    a = DataPreprocess('test.csv')
    # identify_columns()

if __name__ == "__main__":
    main()
