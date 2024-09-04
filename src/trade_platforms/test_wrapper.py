from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from gui.popup import show_error_box
from os.path import exists
import time
import random
from typing import Callable

from trade_platforms.validation_wrapper import ValidationWrapper
from trade_platforms.binance_wrapper import Binance


def _parse_resolution(resolution):
    if resolution == '15m':
        return 15
    if resolution == '1m':
        return 1


def fragment_candle(candle):
    diff = int(abs(candle['open'] - candle['close']))
    fragments = [0]
    sum = 0
    for _ in range(1, 15):
        fragment = random.randint(-30, 30)
        fragments.append(fragment)
        sum += fragment

    if sum != 0 and diff != 0:
        ratio = (sum / diff)
    elif sum == 0 and diff != 0:
        fragments[0] = -fragments[0]
        sum += 2 * fragments[0]
        ratio = (sum / diff)
    elif sum != 0 and diff == 0:
        ratio = (sum / (diff + 0.1))
    else:
        ratio = 1

    final_fragments = []
    for fragment in fragments:
        fragment /= ratio
        if sum != 0 and diff == 0:
            fragment -= (0.1 / 15)
        final_fragments.append(fragment)

    sum = 0
    for fragment in final_fragments:
        sum += fragment

    return final_fragments


## Test platform client wrapper.
#  Simulates platform behavior using pregenerated test data.
#  No connection is used to a real platform.
class TestWrapper(ValidationWrapper):
    def __init__(self, platforms, resolution_sec=60):
        super(TestWrapper, self).__init__(platforms, "TestWrapper")
        # Stores the test data set the wrapper will feed to the bot.
        self.test_data = None
        # Start time of test data playback
        self.start_time = datetime(2021, 2, 1, 0, 0)
        # End time of test data playback.
        self.end_time = datetime(2021, 2, 2, 0, 0)
        # Test data location.
        self.test_data_location = None
        # Overall progress (for calculating progress percentage)
        self.time_progress = self.start_time
        # Data is stored in chunks (for example daily),
        # this progress count contains the progress
        # of processing a single chunk. It is reset to 0 on a new chunk.
        self.row_progress = 0
        self.candle_progress = 0
        self.candle_fragments = []
        ## See @PlatformWrapper
        self.allow_cycle_progress_print = False
        # Current chunk
        self.current_chunk = None
        self.accumulated_history_candles = pd.DataFrame({
            "close": [],
            "high": [],
            "low": [],
            "open": [],
            "startTime": [],
            "volume": []
        })
        self.candle_plot = None
        # Stores the candle resolution in minutes.
        self.resolution_sec = resolution_sec
        # When replaying historical data it is possible that some frames are missing.
        # This counter keeps count of those.
        self.missing_element_count = 0
        # Stores the historical data that has been already processed in the run.
        if isinstance(self.platform, Binance):
            self.candle_history = pd.DataFrame({
                "startTime": [],
                "open": [],
                "high": [],
                "low": [],
                "close": [],
                "volume": [],
                "closeTime": [],
                "quoteAssetVolume": [],
                "noOfTrades": [],
                "takerByBaseAssetVol": [],
                "takerByQuoteAssetVol": [],
                "ignore": []
            })

    ## Sets the start and end time of the loadable test data.
    #  @param test_data_location test data location
    #  @param start_time test data feed starting time
    #  @param end_time test data feed end time
    def set_data_interval(self, test_data_location, start_time, end_time):
        self.test_data_location = test_data_location
        self.test_data = pd.HDFStore(self.test_data_location)['data']
        self.test_data = self.test_data.reset_index(drop=True)
        self.start_time = start_time
        self.end_time = end_time
        if self.start_time == self.end_time:
            raise Exception(
                "set_data_interval(): Start and end times are the same")
        self.time_progress = self.start_time
        start = pd.to_datetime(start_time)
        self.row_progress = \
            self.test_data.index[self.test_data['startTime'] == start].values[0]

    def _accumulate_history_candles(self, data, resolution):
        data = data.iloc[0]
        if len(self.accumulated_history_candles) == 0:
            self.accumulated_history_candles = data
            return self.accumulated_history_candles

        if data['high'] > self.accumulated_history_candles['high']:
            self.accumulated_history_candles['high'] = data['high']
        if data['low'] < self.accumulated_history_candles['low']:
            self.accumulated_history_candles['low'] = data['low']
        self.accumulated_history_candles['volume'] += data['volume']
        time_diff = data['startTime'] - self.accumulated_history_candles['startTime']
        if time_diff >= timedelta(minutes=_parse_resolution(resolution)):
            self.accumulated_history_candles = data
        self.accumulated_history_candles['close'] = data['close']
        return self.accumulated_history_candles

    def historical_data(self, start_time, end_time, resolution_sec):
        """Returns the historical test data."""
        return self.candle_history[
            self.candle_history['startTime'] >= start_time]

    # Updates the current cycle timestamp.
    def update_cycle_timestamp(self):
        self.cycle_timestamp = self.time_progress

    def fetch_current_price(self):
        """
            Returns the current market ask. In test mode
            that is the closing price of the candle.
        """
        return self.current_data['close']

    def get_candle_opening_price(self):
        return self.current_data['open']

    ## Returns the current candle
    def get_current_candle(self, market=None):
        return self.current_data

    ## Returns the simulation start timestamp.
    def get_start_timestamp(self):
        return self.start_time

    ## Fetches the orderbook from test data set.
    def fetch_orderbook(self, depth):
        return (None, None)

    ## Plots the historical data
    #  @param start_date Not used
    #  @param end_date Not used
    #  @param resolution Not used
    def plot_historical(self, start_date=None, end_date=None, resolution=None):
        df = self.candle_history

        self.candle_plot = go.Figure()
        self.candle_plot.update_layout(
            title={
                'text': "USD/BTC",
                'x': 0.5,
                'xanchor': 'center'
            },
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False
        )
        self.candle_plot.add_trace(
            go.Candlestick(
                x=df['startTime'],
                open=df['open'],
                high=df['high'],
                low=df['low'],
                close=df['close']
            )
        )

    def get_candle_plot(self):
        return self.candle_plot

    def show_candles(self):
        self.candle_plot.show()

    ## Executes sell/buy action on a single order.
    #  @param order the single order that needs action.
    def _execute_single_order(self, order):
        if order['side'] == 'buy':
            self._execute_buy(order['price'], order['size'])
            return self._update_order(order, order['size'])
        else:
            self._execute_sell(order['price'], order['size'])
            return self._update_order(order, order['size'])

    ## Evaluate orders.
    #  Currently if it is a market order it will be executed on the average of the current
    #  candle data 'open', 'close' values and if it is limit order, it will
    #  action at order price if it is between the 'open' and 'close' values.
    def evaluate_orders(self):
        if self.get_current_price() >= self.lowest_order_price and \
                self.get_current_price() <= self.highest_order_price:
            # Only interested in orders, those prices are withing the current candle.
            self.orders_of_interest = self.orders[
                (self.orders['status'] != 'closed') &
                (((self.current_data['high'] <= self.current_data['low']) &
                 (self.orders['price'] >= self.current_data['high']) &
                 (self.orders['price'] <= self.current_data['low'])) |
                 ((self.current_data['high'] > self.current_data['low']) &
                 (self.orders['price'] <= self.current_data['high']) &
                 (self.orders['price'] >= self.current_data['low'])))]

            self.orders_of_interest = \
                self.orders_of_interest.apply(self._execute_single_order, axis=1)
            self.order_placed = False
            # # Throw away closed orders to increase performance.
            # self.orders = self.orders[
            #     ((self.current_data['open'] <= self.current_data['close']) &
            #      ((self.orders['price'] < self.current_data['open']) |
            #      (self.orders['price'] > self.current_data['close']))) |
            #     ((self.current_data['open'] > self.current_data['close']) &
            #      ((self.orders['price'] > self.current_data['open']) |
            #      (self.orders['price'] < self.current_data['close'])))]

            # Instead of removing closed orders, they state will change to closed
            self.orders = pd.concat([self.orders, self.orders_of_interest])
            self.orders = self.orders[self.orders['status'] == 'closed']

    def evaluate(self, trade: Callable[[], None]) -> tuple:
        """
            Evaluates test wrapper tasks.

            Parameters:
                - trade (function): is a function callback to the user implemented
                  trading or signalling logic.

            Returns:
                - running (bool): retruns true if the bot is till running.
                - progress_time (int): returns the current progerss time.
        """
        begin = time.time()
        if not exists(self.test_data_location):
            show_error_box("Dataset does not exist")
            return (False, self.time_progress)

        # Finish simulation when it is at the end of the data set.
        if self.time_progress > self.end_time:
            return (False, self.time_progress)

        # Calculate progress.
        percentage = ((self.time_progress - self.start_time) /
                      (self.end_time - self.start_time)) * 100

        self.current_data = self.test_data.loc[self.row_progress]
        self.candle_history = pd.concat(
            [self.candle_history, pd.DataFrame([self.current_data])])

        (running, _) = super().evaluate(trade)
        self.time_progress += timedelta(seconds=self.resolution_sec)
        # if self.candle_progress >= 15:
        #     self.candle_progress = -1
        self.row_progress += 1
        # self.candle_progress += 1

        end = time.time()
        print(f"{percentage:.3f}% \
exec time: {end - begin:.3f}, date: {self.current_data['startTime'] + timedelta(seconds=self.resolution_sec)}, \
orders: {len(self.orders)} {self.cyclic_message_appendix}")

        return (running, self.time_progress)
