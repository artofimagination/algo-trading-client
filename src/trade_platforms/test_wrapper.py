from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go
from popup import show_error_box
from os.path import exists
import time

from trade_platforms.validation_wrapper import ValidationWrapper


## Test platform client wrapper.
#  Simulates platform behavior using pregenerated test data.
#  No connection is used to a real platform.
class TestWrapper(ValidationWrapper):
    def __init__(self):
        super(TestWrapper, self).__init__(None, "TestWrapper")
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
        ## See @PlatformWrapper
        self.allow_cycle_progress_print = False
        # Current chunk
        self.current_chunk = None
        # When replaying historical data it is possible that some frames are missing.
        # This counter keeps count of those.
        self.missing_element_count = 0
        # Stores the historical data that has been already processed in the run.
        self.candle_history = pd.DataFrame({
            "close": [],
            "high": [],
            "low": [],
            "open": [],
            "startTime": [],
            "volume": []
        })

    ## Sets the start and end time of the loadable test data.
    #  @param test_data_location test data location
    #  @param start_time test data feed starting time
    #  @param end_time test data feed end time
    def set_data_interval(self, test_data_location, start_time, end_time):
        self.test_data_location = test_data_location
        self.test_data = pd.HDFStore(self.test_data_location)['data']
        self.start_time = start_time
        self.end_time = end_time
        if self.start_time == self.end_time:
            raise Exception(
                "set_data_interval(): Start and end times are the same")
        self.time_progress = self.start_time

    ## Returns the historical test data.
    def historical_data(self, start_time, end_time, resolution):
        start = pd.to_datetime(datetime.fromtimestamp(start_time))
        return self.candle_history[
            self.candle_history['startTime'] >= start]

    # Updates the current cycle timestamp.
    def update_cycle_timestamp(self):
        self.cycle_timestamp = self.time_progress

    ## Returns the current market ask. In test mode
    # That is the average of open and close values
    def fetch_current_price(self):
        return (self.current_data['open'] + self.current_data['close']) / 2.0

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

        fig = go.Figure()
        fig.update_layout(
            title={
                'text': "USD/BTC",
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

    ## Executes sell/buy action on a single order.
    #  @param order the single order that needs action.
    def _execute_single_order(self, order):
        if order['side'] == 'buy':
            self._execute_buy(order['type'], order['price'], order['size'])
            return self._update_order(order, order['size'])
        else:
            self._execute_sell(order['type'], order['price'], order['size'])
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
                ((self.current_data['open'] <= self.current_data['close']) &
                 (self.orders['price'] >= self.current_data['open']) &
                 (self.orders['price'] <= self.current_data['close'])) |
                ((self.current_data['open'] > self.current_data['close']) &
                 (self.orders['price'] <= self.current_data['open']) &
                 (self.orders['price'] >= self.current_data['close']))]

            self.orders_of_interest = \
                self.orders_of_interest.apply(self._execute_single_order, axis=1)

            # Throw away closed orders to increase performance.
            self.orders = self.orders[
                ((self.current_data['open'] <= self.current_data['close']) &
                 ((self.orders['price'] < self.current_data['open']) |
                 (self.orders['price'] > self.current_data['close']))) |
                ((self.current_data['open'] > self.current_data['close']) &
                 ((self.orders['price'] > self.current_data['open']) |
                 (self.orders['price'] < self.current_data['close'])))]

    ## Evaluates test wrapper tasks.
    #  @param trade is a function callback to the user implemented
    #               trading or signalling logic.
    def evaluate(self, trade):
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

        self.current_data = self.test_data.iloc[self.row_progress]
        # Accumulate candle history for potential user processing.
        self.candle_history = self.candle_history.append(self.current_data)
        self.row_progress += 1
        self.time_progress += timedelta(seconds=15)

        (running, _) = super().evaluate(trade)

        end = time.time()
        print(f"{percentage:.3f}% \
exec time: {end - begin:.3f}, date: {self.time_progress}, orders: {len(self.orders)}")

        return (running, self.time_progress)
