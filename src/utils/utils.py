import os
import yaml
import openai
from json import JSONDecoder
import pickle
from dateutil.parser import parse
from datetime import timedelta


global_config = {}

def initialize(config_path):
    with open(config_path,'r') as f:
        config = yaml.safe_load(f)
    os.environ["http_proxy"] = config['http_proxy']
    os.environ["https_proxy"] = config['https_proxy']
    openai.api_key = config['api_key']
    openai.api_base = config['api_base']
    global_config.update(config)
def extract_json_objects(text, decoder=JSONDecoder()):
    """Find JSON objects in text, and yield the decoded JSON data

    Does not attempt to look for JSON arrays, text, or other JSON types outside
    of a parent JSON object.

    """
    pos = 0
    while True:
        match = text.find('{', pos)
        if match == -1:
            break
        try:
            result, index = decoder.raw_decode(text[match:])
            yield result
            pos = match + index
        except ValueError:
            pos = match + 1
def get_timedelta(dic):
    return timedelta(days=0, seconds=0, microseconds=0,milliseconds=0, minutes=dic['TimeFitness'], hours=0, weeks=0)
def print_dic_info(dic, dic_name, tag=''):
    for k in dic:
        print(tag, end='')
        if type(dic[k])==type({}):
            print(f'{dic_name}[{k}]:{type(dic[k])}'+'{')
            print_dic_info(dic[k], f'{dic_name}[{k}]', tag=tag+'\t')
            print('}', end='')
        elif 'numpy' in str(type(dic[k])):
            print(f'{dic_name}[{k}]:{type(dic[k])}  (shape={dic[k].shape})', end='')
        elif type(dic[k])== type([]):
            lis = dic[k]
            s = f'({len(lis)}, {len(lis[0])})' if len(lis)>0 and type(lis[0])==type([]) else f'{len(lis)}'
            print(f'{dic_name}[{k}]:{type(dic[k])}  (len={s})', end='')
        else:
            print(f'{dic_name}[{k}]:{type(dic[k])}', end='')
        print()

def build_uctb_dataset(traffic_node, time_fitness, node_station_info, start_time, end_time, dataset_name,
    traffic_monthly_interaction=None, external_feature_weather=None, node_poi=None, 
    traffic_grid=None, grid_lat_lng=None, gird_poi=None, print_dataset=False, output_dir=None):
    """
    build and return the uctb dataset in dic format
    necessary:
        time_fitness
        time_range
        Node
            traffic_node
            node_satation_info          
        
    optional: 
        Node
            traffic_monthly_interaction
            poi
        Grid
            traffic_grid
            gird_lat_lng
            poi
        ExternalFeature
            Weather
    """
    dataset = {'TimeRange':f'[{start_time},{end_time}]', 'TimeFitness':time_fitness, 'Node':{'TrafficNode':traffic_node, 'StationInfo':node_station_info},
                    'Grid':{}, 'ExternalFeature':{}, 'LenTimeSlots':traffic_node.shape[0]}

    # make sure no data missing in traffic node
    print(start_time)
    print(end_time)
    print(dataset['Node']['TrafficNode'].shape[0])
    beg_dt = parse(start_time)
    # assert beg_dt+(dataset['Node']['TrafficNode'].shape[0])*get_timedelta(dataset) == parse(end_time)

    dataset['Node']['TrafficMonthlyInteraction'] = traffic_monthly_interaction
    dataset['Grid']['TrafficGrid'] = traffic_grid
    dataset['Grid']['GridLatLng'] = grid_lat_lng
    dataset['ExternalFeature']['Weather'] = [] if external_feature_weather is None else external_feature_weather
    
    if node_poi is not None:
        dataset['Node']['POI'] = node_poi
        
    if gird_poi is not None:
        dataset['Grid']['POI'] = gird_poi
    
    if print_dataset:
        print_dic_info(dataset, 'dataset')

    if output_dir is None:
        pkl_file_name = f'{dataset_name}.pkl'
    else:
        pkl_file_name = os.path.join(output_dir, '{}.pkl'.format(dataset_name))

    with open(pkl_file_name, 'wb') as f:
        pickle.dump(dataset, f)