import pandas as pd

"""
Station from 0 begin
"""

class NodeStationInfoBuilding:
    '''
    Build info for node
    '''
    def __init__(self, filename, nodelist, list_index=None):
        self.filename = filename
        self.nodelist = nodelist
        self.list_index = list_index
        self.filepath = f'./user_data/preprocessed_data/preprocessed_{filename}.csv'

    def extract(self):
        '''
        Extract and process node info from the CSV file.
        
        :return: Processed DataFrame with node info.
        '''
        df = pd.read_csv(self.filepath)
        # Keep only the columns specified in self.nodelist
        df = df[self.nodelist]
        # Remove duplicate rows
        df = df.drop_duplicates()
        
        # Sort the DataFrame based on list_index if provided
        if self.list_index is not None and self.list_index in df.columns:
            df = df.sort_values(by=self.list_index)
            # If the index is the same, keep only the first row
            df = df.drop_duplicates(subset=self.list_index, keep='first')
            df['ind'] = range(0, len(df))
        else:
            # If list_index is None, create a new index column
            df['ind'] = range(0, len(df))
        
        return df

    def to_dict_list(self, df):
        '''
        Convert DataFrame to a list of dictionaries with 'ind' as key.
        
        :param df: DataFrame to be converted.
        :return: List of dictionaries.
        '''
        dict_list = []
        for index, row in df.iterrows():
            row_dict = row.to_dict()
            dict_list.append(row_dict)
        return dict_list

class GridLatLngBuilding:
    def __init__(self, filename, latcol, lngcol):
        self.filename = filename
        self.latcol = latcol
        self.lngcol = lngcol
        self.filepath = f'./user_data/preprocessed_data/preprocessed_{filename}.csv'

    def build_grid(self):
        '''
        Placeholder method for building grid.
        '''
        pass

if __name__ == "__main__":
    TEST = 2
    if TEST == 1:
        filename = 'Bike_DC'
        nodelist = ['start_station_id', 'start_station_name', 'start_lng', 'start_lat']
        list_index = 'start_station_id'
        
        node_info_builder = NodeStationInfoBuilding(filename, nodelist, list_index)
        extracted_df = node_info_builder.extract()
        print(extracted_df)
    elif TEST == 2:
        filename = 'Bike_DC'
        nodelist = ['start_station_id', 'start_station_name', 'start_lng', 'start_lat']
        list_index = 'start_station_id'
        
        node_info_builder = NodeStationInfoBuilding(filename, nodelist, list_index)
        extracted_df = node_info_builder.extract()
        a = node_info_builder.to_dict_list(extracted_df)
        print(a)