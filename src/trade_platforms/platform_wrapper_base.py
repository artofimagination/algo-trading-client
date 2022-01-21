from typing import List
from enum import Enum


# Enum to identify platforms
class Platforms(Enum):
    FTX = "FTX"


class PlatformWrapper():
    def __init__(self, name):
        self.name = name
        ## Wait time between cycles.
        self.sleep_time = 2

    def place_order(self):
        pass

    def plot_historical(self, start_date, end_date, resolution):
        pass

    def cancel_order(self):
        pass

    def get_current_price(self):
        pass

    def evaluate(self):
        return (True, None, None)

    def get_order_history(self, side, order_type, start_time, end_time) -> List[dict]:
        return None

    def get_account_info(self):
        return None

    def get_balances(self):
        return None

    def cleanup_iteration(self):
        pass

    def get_start_timestamp(self):
        return None

    def set_data_interval(self, start_time, end_time):
        pass

    def set_start_balance(self, balance_USD):
        pass

    ## Sets the wait time between cycles when running the platform.
    def set_wait_time(self, sleep_seconds):
        self.sleep_time = sleep_seconds
