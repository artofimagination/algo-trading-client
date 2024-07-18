from datetime import datetime
from typing import List
from enum import Enum
import pandas as pd
import time
import plotly.graph_objects as go


## Enum to identify platforms
class Platforms(Enum):
    FTX = "FTX"
    Binance = "Binance"


## Base class for platfrom wrappers.
# Implements all common functionalities
# for platforms and platform simulators
class PlatformWrapper():
    def __init__(self, name):
        self.name = name
        ## Wait time between cycles.
        self.sleep_time = 2
        ## Storing the current price, to reduce the number of REST gets.
        #  Value is updated once per cycle.
        self.current_price = 0
        ## Cycle count.
        self.cycle = 0
        ## Enables cycle progress print
        self.allow_cycle_progress_print = True
        ## Stores the current cycle timestamp
        self.cycle_timestamp = datetime.now()
        ## Holds the current candle closing price.
        self.current_candle_closing_price = 0
        ## Holds the current bids of the orderbook.
        self.current_bids = None
        ## holds the current asks of the orderbook.
        self.current_asks = None
        ## Stores the start time of the run
        self.start_time = datetime.now()
        ## Message showing details every cycle.
        self.cyclic_message_appendix = ''

    # Interface to place_order.
    def place_order(self):
        pass

    def get_order(self, order_id):
        pass

    ## Get plotting historical data
    #  @param start_time starting date of the data
    #  @param end_time end date of the data
    #  @param resolution of the data
    def plot_historical(self, start_time=None, end_time=None, resolution=None):
        df = self.historical_data(start_time, end_time, resolution)
        # Convert time to date
        df['date'] = pd.to_datetime(
            df['time'] / 1000, unit='s', origin='unix'
        )

        fig = go.Figure()
        fig.update_layout(
            title={
                'text': "Result",
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False
        )
        fig.add_trace(
            go.Candlestick(
                x=df['startTime'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close']
            )
        )
        fig.show()

    ## Interface for cancel_order.
    def cancel_order(self):
        pass

    ## Returns the fetched price.
    def get_current_price(self):
        return self.current_price

    def get_candle_opening_price(self):
        return None

    def get_current_candle(self):
        return None

    ## Fetches the current market price from remote.
    #  Implemented on real platform wrappers.
    def fetch_current_price(self):
        pass

    ## Returns the orderbook.
    def get_orderbook(self):
        return (self.current_bids, self.current_asks)

    ## Fetches the orderbook from remote.
    #  Implemented on real platform wrappers.
    def fetch_orderbook(self, depth):
        pass

    ## Returns the current cycle timestamp.
    def get_cycle_timestamp(self):
        return self.cycle_timestamp

    ## Appends additional info to the cyclic print
    def append_to_cyclic_message(self, message):
        self.cyclic_message_appendix = message

    ## Updates the current cycle timestamp.
    #  Implementation differs in Test, Validation and Production modes.
    def update_cycle_timestamp(self):
        self.cycle_timestamp = datetime.now()

    ## Evaluates processes common for all type of platforms.
    def evaluate(self, trade):
        self.update_cycle_timestamp()
        (self.current_bids, self.current_asks) = self.fetch_orderbook(100)
        if self.allow_cycle_progress_print:
            print(f"Cycle: {self.cycle}, \
time: {self.cycle_timestamp}, orders: {len(self.get_order_history())} \
{self.cyclic_message_appendix}")
            self.cycle += 1
        self.current_price = self.fetch_current_price()
        if self.sleep_time > 0:
            time.sleep(self.sleep_time)
        running = True
        if trade is not None:
            running = trade()
        return (running, self.cycle_timestamp)

    ## Interface for get_order_history
    def get_order_history(
            self,
            side=None,
            order_type=None,
            start_time=None,
            end_time=None) -> List[dict]:
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
