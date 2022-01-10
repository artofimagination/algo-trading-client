from dotenv import load_dotenv
import os
import pandas as pd
import plotly.graph_objects as go
import requests
from typing import List
from trade_platforms.ftx_client import FtxClient
from trade_platforms.platform_wrapper_base import PlatformWrapper


## FTX wrapper on the original ftx client from here
#  https://github.com/ftexchange/ftx/blob/master/rest/client.py
class FTX(PlatformWrapper):
    def __init__(self, base_currency, quote_currency):
        super(FTX, self).__init__(f'FTX-{base_currency}-{quote_currency}')
        self.api_url = 'https://ftx.com/api/markets'
        # Load env to get API key
        load_dotenv()
        self.api_key = os.getenv("FTX_API_KEY")
        self.api_secret = os.getenv("FTX_API_SECRET")
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        if self.base_currency is None or self.quote_currency is None:
            raise Exception(f"Market not selected. \"base_currency\" is {self.base_currency}\
and \"quote_currency\" is {self.quote_currency}")

    ## Returns the market data.
    def market_data(self):
        # Specify the base and quote currencies to get single market data
        request_url = f'{self.api_url}/{self.base_currency}/{self.quote_currency}'
        return pd.DataFrame(requests.get(request_url).json())

    ## Get historical data
    #  @param start_date starting date of the data
    #  @param end_date end date of the data
    #  @param resolution of the data
    def historical_data(self, start_date, end_date, resolution):
        # Specify the base and quote currencies to get single market data
        request_url = f'{self.api_url}/{self.base_currency}/{self.quote_currency}'

        if end_date is None:
            request = \
                f'{request_url}/candles?resolution={resolution}&start_time={start_date}'
        else:
            request = \
                f'{request_url}/candles?resolution={resolution}\
&start_time={start_date}&end_time={end_date}'
        # Get the historical market data as JSON
        historical = requests.get(request).json()

        # Convert JSON to Pandas DataFrame
        return pd.DataFrame(historical['result'])

    ## Returns the order history.
    #  @param side filter by side ("buy"/"sell")
    #  @param order_type filter by type order ("limit")
    #  @param start_time starting date of the history
    #  @param end_time end date of the history.
    def get_order_history(
            self,
            side: str = None,
            order_type: str = None,
            start_time: float = None,
            end_time: float = None) -> List[dict]:
        return pd.DataFrame(self.get_order_history(
            f"{self.base_currency}/{self.quote_currency}",
            side,
            order_type,
            start_time,
            end_time))

    ## Get plotting historical data
    #  @param start_date starting date of the data
    #  @param end_date end date of the data
    #  @param resolution of the data
    def plot_historical(self, start_date=None, end_date=None, resolution=None):
        df = self.historical_data(start_date, end_date, resolution)
        # Convert time to date
        df['date'] = pd.to_datetime(
            df['time'] / 1000, unit='s', origin='unix'
        )
        # Remove unnecessary columns
        df.drop(['startTime', 'time'], axis=1, inplace=True)

        fig = go.Figure()
        fig.update_layout(
            title={
                'text': f"{self.base_currency}/{self.quote_currency}",
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

    ## Places the order
    #   @param side   the value can be "sell" or "buy"
    #   @param price  price of the order
    #   @param volume volume of the order
    def placeOrder(self, side, price, volume):
        ftx_client = FtxClient(
            api_key=self.api_key,
            api_secret=self.api_secret)
        # Place an order
        try:
            order_result = ftx_client.place_order(
                market=f"{self.base_currency}/{self.quote_currency}",
                side=side,
                price=price,
                size=volume
            )
        except Exception as e:
            print(f'Error making order request: {e}')
            return None
        return order_result

    ## Cancels the order
    def cancelOrder(self, order):
        ftx_client = FtxClient(
            api_key=self.api_key,
            api_secret=self.api_secret)
        try:
            co_result = ftx_client.cancel_order(
                order_id=order['id']
            )
            print(co_result)
        except Exception as e:
            print(f'Error cancelling order request: {e}')

    ## Returns the market ask.
    def marketAsk(self):
        request_url = f'{self.api_url}/{self.base_currency}/{self.quote_currency}'
        market = requests.get(request_url).json()
        market_ask = market['result']['ask']
        print(f"{self.base_currency}/{self.quote_currency} asking price = {market_ask}")
        return market_ask
