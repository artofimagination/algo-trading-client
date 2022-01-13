from typing import List


class PlatformWrapper():
    def __init__(self, name):
        self.name = name

    def placeOrder(self):
        pass

    def plot_historical(self, start_date, end_date, resolution):
        pass

    def cancelOrder(self):
        pass

    def marketAsk(self):
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
