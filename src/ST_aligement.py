import os
import pandas as pd
import pyproj
import pytz
from tqdm import tqdm
from dateutil import parser
from coord_convert.transform import wgs2gcj, gcj2wgs

# Define project root and data directories
project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
preprocessed_data_dir = os.path.join(project_root, 'user_data', 'preprocessed_data')
metadata_dir = os.path.join(project_root, 'user_data', 'metadata')

# Define coordinate systems
WGS84 = pyproj.CRS('EPSG:4326')
NAD83 = pyproj.CRS('EPSG:4269')
CGCS2000 = pyproj.CRS('EPSG:4490')

# Create a dictionary of transformers for coordinate system conversions
TRANSFORMERS = {
    ('WGS84', 'NAD83'): pyproj.Transformer.from_crs(WGS84, NAD83, always_xy=True),
    ('NAD83', 'WGS84'): pyproj.Transformer.from_crs(NAD83, WGS84, always_xy=True),
    ('WGS84', 'CGCS2000'): pyproj.Transformer.from_crs(WGS84, CGCS2000, always_xy=True),
    ('CGCS2000', 'WGS84'): pyproj.Transformer.from_crs(CGCS2000, WGS84, always_xy=True),
    ('NAD83', 'CGCS2000'): pyproj.Transformer.from_crs(NAD83, CGCS2000, always_xy=True),
    ('CGCS2000', 'NAD83'): pyproj.Transformer.from_crs(CGCS2000, NAD83, always_xy=True),
}

class DatasetAlignment:
    """Base class for dataset alignment operations."""

    def __init__(self, filename, col, frm, to):
        """
        Initialize the DatasetAlignment instance.

        :param filename: Name of the file to be processed.
        :param col: Column(s) to be processed.
        :param frm: Source format or timezone.
        :param to: Target format or timezone.
        """
        self.filename = filename
        self.preprocessed_file_path = os.path.join(preprocessed_data_dir, f'preprocessed_{filename}.csv')
        self.frm = frm
        self.to = to
        self.col = col

class SpatialAlignment(DatasetAlignment):
    """Class used to convert a column from one coordinate system to another."""

    def __init__(self, filename, col, frm, to):
        """
        Initialize the SpatialAlignment instance.

        :param filename: Name of the file to be processed.
        :param col: Column(s) to be processed.
        :param frm: Source coordinate system.
        :param to: Target coordinate system.
        """
        super().__init__(filename, col, frm, to)

    def convert_coordinates(self, transformer, lat, lon):
        """
        Convert coordinates using the provided transformer.

        :param transformer: Transformer object for coordinate conversion.
        :param lat: Latitude.
        :param lon: Longitude.
        :return: Converted latitude and longitude.
        """
        x, y = transformer.transform(lon, lat)
        return y, x

    def transform_df(self, df, columns, from_format, to_format):
        """
        Transform the DataFrame columns from one format to another.

        :param df: DataFrame to be transformed.
        :param columns: Columns to be transformed.
        :param from_format: Source format.
        :param to_format: Target format.
        :return: Transformed DataFrame.
        """
        tqdm.pandas()
        if from_format == 'WGS84' and to_format == 'GCJ02':
            df[columns] = df[columns].progress_apply(lambda coord: wgs2gcj(*coord), axis=1)
        elif from_format == 'GCJ02' and to_format == 'WGS84':
            df[columns] = df[columns].progress_apply(lambda coord: gcj2wgs(*coord), axis=1)
        elif from_format == 'GCJ02':
            df[columns] = df[columns].progress_apply(lambda coord: gcj2wgs(*coord), axis=1)
            self.transform_df(df, columns, 'WGS84', to_format)
        elif to_format == 'GCJ02':
            self.transform_df(df, columns, from_format, 'GCJ02')
            df[columns] = df[columns].progress_apply(lambda coord: wgs2gcj(*coord), axis=1)
        elif (from_format, to_format) in TRANSFORMERS:
            transformer = TRANSFORMERS[(from_format, to_format)]
            df[columns] = df[columns].progress_apply(lambda coord: pd.Series(self.convert_coordinates(transformer, *coord)), axis=1)
        else:
            raise ValueError(f"Unsupported conversion from {from_format} to {to_format}")
        return df

    def spatial_alignment(self):
        """Perform spatial alignment on the dataset."""
        df = pd.read_csv(self.preprocessed_file_path)
        self.transform_df(df, self.col, self.frm, self.to)
        df.to_csv(self.preprocessed_file_path, index=False)

class TimeZoneConverter(DatasetAlignment):
    """Class used to convert a column from one timezone to another."""

    def __init__(self, filename, col, frm, to):
        """
        Initialize the TimeZoneConverter instance.

        :param filename: Name of the file to be processed.
        :param col: Column to be processed.
        :param frm: Source timezone.
        :param to: Target timezone.
        """
        super().__init__(filename, col, frm, to)
        self.timezones = pytz.all_timezones

    def convert_timezone(self, date_str, from_tz, to_tz):
        """
        Convert the timezone of a date string.

        :param date_str: Date string to be converted.
        :param from_tz: Source timezone.
        :param to_tz: Target timezone.
        :return: Converted date string.
        """
        dt = parser.parse(date_str)
        dt = from_tz.localize(dt)
        dt = dt.astimezone(to_tz)
        return dt.strftime('%Y-%m-%d %H:%M:%S')

    def temporal_alignment(self):
        """Perform temporal alignment on the dataset."""
        if self.frm not in self.timezones or self.to not in self.timezones:
            raise ValueError("Invalid timezone specified.")
        df = pd.read_csv(self.preprocessed_file_path)
        tqdm.pandas(desc="converting...")
        from_tz = pytz.timezone(self.frm)
        to_tz = pytz.timezone(self.to)
        df[self.col] = df[self.col].progress_apply(lambda x: self.convert_timezone(x, from_tz, to_tz))
        df.to_csv(self.preprocessed_file_path, index=False)

if __name__ == "__main__":
    TESTCODE = 2
    if TESTCODE == 1:
        # Example usage
        filename = 'Bike_DC'
        col = ['start_lat', 'start_lng']
        frm = 'WGS84'
        to = 'NAD83'

        # Create SpatialAlignment instance and perform spatial alignment
        spatial_aligner = SpatialAlignment(filename, col, frm, to)
        spatial_aligner.spatial_alignment()
    elif TESTCODE == 2:
        filename = 'Bike_DC'
        col = 'started_at'
        # Create TimeZoneConverter instance and perform temporal alignment
        timezone_converter = TimeZoneConverter(filename, col, 'Europe/London', 'America/New_York')
        timezone_converter.temporal_alignment()