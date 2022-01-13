from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go

from trade_platforms.validation_wrapper import ValidationWrapper


## Test platform client wrapper.
#  Simulates platform behavior using pregenerated test data.
#  No connection is used to a real platform.
class TestWrapper(ValidationWrapper):
    def __init__(self):
        super(TestWrapper, self).__init__("TestWrapper")
        # Stores the test data set the wrapper will feed to the bot.
        self.testData = None
        # Start time of test data playback
        self.start = datetime(2021, 2, 1, 0, 0)
        # End time of test data playback.
        self.end = datetime(2021, 2, 2, 0, 0)
        # Current test data playback timestamp
        self.timestamp = self.start
        # Overall progress (for calculating progress percentage)
        self.overall_progress = self.start
        # Data is stored in chunks (for example daily),
        # this progress count contains the progress
        # of processing a single chunk. It is reset to 0 on a new chunk.
        self.chunk_progress = 0
        # Previous data of the processing
        self.previous_data = None
        # Stores the historical data that has been already processed in the run.
        self.historical_data = pd.DataFrame({
            "close": [],
            "high": [],
            "low": [],
            "open": [],
            "startTime": [],
            "volume": []
        })
        # Simulated user account info.
        self.account_info = {
            "backstopProvider": True,
            "collateral": 2000,
            "freeCollateral": 1786071.456884368,
            "initialMarginRequirement": 0.12222384240257728,
            "leverage": 10,
            "liquidating": False,
            "maintenanceMarginRequirement": 0.07177992558058484,
            "makerFee": 0.0002,
            "marginFraction": 0.5588433331419503,
            "openMarginFraction": 0.2447194090423075,
            "takerFee": 0.004,
            "totalAccountValue": 3568180.98341129,
            "totalPositionSize": 6384939.6992,
            "username": "user@domain.com",
            "positions": [
                {
                    "cost": -31.7906,
                    "entryPrice": 138.22,
                    "future": "ETH-PERP",
                    "initialMarginRequirement": 0.1,
                    "longOrderSize": 1744.55,
                    "maintenanceMarginRequirement": 0.04,
                    "netSize": -0.23,
                    "openSize": 1744.32,
                    "realizedPnl": 3.39441714,
                    "shortOrderSize": 1732.09,
                    "side": "sell",
                    "size": 0.23,
                    "unrealizedPnl": 0
                }
            ]
        }

    ## Sets the start and end time of the loadable test data.
    #  @param start_time test data feed starting time
    #  @param end_time test data feed end time
    def set_data_interval(self, start_time, end_time):
        self.start = start_time
        self.end = end_time

    ## Plots the historical data
    #  @param start_date Not used
    #  @param end_date Not used
    #  @param resolution Not used
    def plot_historical(self, start_date=None, end_date=None, resolution=None):
        df = self.historical_data

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

    ## Returns the current market ask. In test mode
    # That is the open value of the current candle.
    def marketAsk(self):
        return self.previous_data['open']

    ## Returns the simulation start timestamp.
    def get_start_timestamp(self):
        return self.start

    ## Sets the test data set.
    def set_test_data(self, df):
        self.testData = df

    ## Evaluates test wrapper tasks.
    def evaluate(self):
        if self.overall_progress > self.end:
            return (False, None, None)

        percentage = ((self.overall_progress - self.start) /
                      (self.end - self.start)) * 100
        print(f"{percentage:.3f}%")
        timestamp = self.timestamp
        chunk_length = len(self.testData[timestamp.strftime("DF%Y%m%d")])
        super().evaluate()

        self.overall_progress += timedelta(minutes=1)
        if self.chunk_progress == chunk_length:
            self.timestamp += timedelta(minutes=60 * 24)
            self.chunk_progress = 0
        self.previous_data = \
            self.testData[timestamp.strftime("DF%Y%m%d")].loc[self.chunk_progress]
        self.historical_data = self.historical_data.append(self.previous_data)
        self.chunk_progress += 1
        return (True,
                self.previous_data,
                timestamp + timedelta(minutes=self.chunk_progress - 1))
