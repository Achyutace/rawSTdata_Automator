# 半成品
欢迎使用我们的基于LLM的自动处理时空数据工具。本工具用来将未处理的csv格式的交通数据转化成UCTB格式的pkl文件。
- 本工具适用于你想要构建空间-时间二维数据以及经度-维度-时间三维数据。我们提供一套全自动化的数据清洗-数据对齐-数据集构建-可视化检查流程。
- 按照官方文档，一步步跟着指示走即可处理数据。
## 数据集情况
UCTB（Urban Computing and Transportation Branch）是一个为城市计算设计的数据集格式，它包含了多种城市交通相关的数据集，例如共享单车、共享出行、交通速度、行人计数等。根据提供的网页内容，UCTB数据集格式主要包括以下键（Key）及其用途：

TimeRange: 表示数据的时间范围，通常是一个字符串列表，包含开始和结束日期。

TimeFitness: 表示时间粒度，即数据记录的时间间隔长度，通常以分钟为单位。

Node: 包含交通节点相关的信息，是一个字典，可能包含以下子键：

TrafficNode: 交通节点的时空信息，通常是一个NumPy数组，其形状为[时间序列长度, 节点数量]。
TrafficMonthlyInteraction: 交通节点之间的月度交互信息（如果有的话）。
StationInfo: 交通站点的基本信息，如站点ID、建立时间、纬度、经度和名称，通常是一个列表。
POI: 兴趣点（Point of Interest）信息。
Grid: 包含交通网格相关的信息，是一个字典，可能包含以下子键：

TrafficGrid: 交通网格的时空信息。
GridLatLng: 交通网格的经纬度信息。
POI: 网格格式的兴趣点信息。
ExternalFeature: 包含外部特征信息，如天气等，是一个字典，可能包含以下子键：

Weather: 天气信息，通常是一个二维数组，第一维是时间序列长度，第二维是天气特征维度。
UCTB format as below：
```json
my_dataset = {
    "TimeRange": ['YYYY-MM-DD', 'YYYY-MM-DD'],
    "TimeFitness": 60, # Minutes
    
    "Node": {
        "TrafficNode": np.array, # With shape [time, num-of-node]
        "TrafficMonthlyInteraction": np.array, # With shape [month, num-of-node. num-of-node]
        "StationInfo": list # elements in it should be [id, build-time, lat, lng, name]
        "POI": []
    },

    "Grid": {
        "TrafficGrid": [],
        "GridLatLng": [],
        "POI": []
    },

    "ExternalFeature": {
         "Weather": [time, weather-feature-dim]
    }
}
```
## 数据清洗
正常数据清洗，删除副本行，缺失项的行和异常值的行。

## 数据对齐

### 时间坐标对齐
目前支持UTC、GMT和各个国家时区相互转化。按照pytz库的all_timezones的时区名称格式输入即可。

### 空间坐标系对齐
目前支持WGS84，GCJ02，CGCS2000和NAD83相互转化。

## 数据集构建
时空坐标均会自动离散化。
### 构建trafficnode
输入时间列、站点列、站点信息以及时序数列离散化颗粒度即可。
### 构建trafficgrid
输入时间列、经度列、纬度列、grid大小即可。

## 自动化检查数据
还没添加到主功能中，但写好了支持可视化某个node七天情况的代码（待定）