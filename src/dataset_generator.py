from matplotlib import units
from trade_platforms.platform_wrapper_base import Platforms
from trade_platforms.binance_wrapper import Binance
from trade_platforms.platform_wrapper_base import PlatformWrapper

from popup import show_error_box
from os.path import exists
from os import mkdir, remove
import pandas as pd
from datetime import timedelta, datetime


def get_platform_client(platform) -> PlatformWrapper:
    """
        Returns the requested platform client.

        Parameters:
            - platorm (Platforms): The id of the platform to be connected.

        Returns:
            The selected platform wrapper.
    """

    if platform['platform_type'] == Platforms.Binance:
        return Binance(
            base_currency=platform['base_currency'],
            quote_currency=platform['quote_currency'])


def generate_dataset_filename(
        dataset: str, platform: Platforms, start_time: datetime, end_time: datetime, resolution_s: str) -> str:
    """
        Generates a dataset file name based on the platform,
        start/end time and resolution.

        Parameters:
            - dataset (str): Defines the dataset type (for example "candles")
            - platform (Platforms): Defines the platform id the data is generated from.
            - start_time (datetime): defines the start time of the dataset.
            - end_time (datetime): defines the end time of the dataset.
            - resolution_str (str): Stores the resolution of candles to get.

        Return:
            - (str): the path and filename of the dataset.
    """
    start_string = start_time.strftime("%Y%m%d_T%H%M")
    end_string = end_time.strftime("%Y%m%d_T%H%M")
    filename = f"{platform['platform_type'].value}_{platform['base_currency']}_\
{platform['quote_currency']}_{dataset}_{start_string}_{end_string}_{resolution_s}.h5"
    path = "src/bots/data/"
    return f"{path}{filename}"


def generate_candle_historical_dataset(
        platform: Platforms, start_time: datetime, end_time: datetime, resolution_str: str) -> str:
    """
        Generates candle data set from platform historical data.
        Lowest resolution is 15 seconds.

        Parameters:
            - platform (Platforms): Defines the platform id the data is generated from.
            - start_time (datetime): defines the start time of the dataset.
            - end_time (datetime): defines the end time of the dataset.
            - resolution_str (str): Stores the resolution of candles to get.

        Returns:
            - (str): the generated file's name and path
    """
    dataset_file_name = generate_dataset_filename(
        "candles", platform, start_time, end_time, resolution_str)
    if exists(dataset_file_name):
        print("Dataset already created")
        return dataset_file_name

    if not exists('src/bots/data'):
        mkdir('src/bots/data')

    timestamp = start_time
    store = pd.HDFStore(dataset_file_name)
    try:
        while timestamp < end_time:
            start_date = timestamp
            if platform['platform_type'] == Platforms.Binance:
                # Data is always stored in 1000 minutes chunks
                timestamp += timedelta(minutes=15 * 1000)
            end_date = timestamp

            platform_client = get_platform_client(platform)
            df = platform_client.historical_data(
                start_time=start_date.timestamp(),
                end_time=None,
                resolution=resolution_str)
            if platform['platform_type'] == Platforms.FTX:
                df['startTime'] = pd.to_datetime(
                    df['startTime'],
                    format="%Y-%m-%dT%H:%M:%S+00:00")
            df['startTime'] = pd.to_datetime(
                df['startTime'],
                unit='ms')
            print(f"Get data from {str(start_date)} to {str(end_date)} len {len(df)}")
            store.append("data", df)
            timestamp += timedelta(seconds=1)
        store.close()
    except Exception as e:
        show_error_box(e)
        remove(dataset_file_name)
        return None
    return dataset_file_name
