from datetime import datetime
from dotenv import load_dotenv
import os
import pandas as pd
import plotly.graph_objects as go
import requests
from trade_platforms.ftx_client import FtxClient
from trade_platforms.platform_wrapper_base import PlatformWrapper

class FTX(PlatformWrapper):
    def __init__(self, name, base_currency, quote_currency):
        super(FTX, self).__init__(name)
        self.api_url = 'https://ftx.com/api/markets'
        # Load env to get API key
        load_dotenv()
        self.api_key = os.getenv("FTX_API_KEY")
        self.api_secret = os.getenv("FTX_API_SECRET")
        self.base_currency = base_currency
        self.quote_currency = quote_currency
    
    def getAllMarket(self):
        # Get all market data as JSON
        all_markets = requests.get(self.api_url).json()
        # Convert JSON to Pandas DataFrame
        df = pd.DataFrame(all_markets['result'])
        df.set_index('name', inplace = True)
        print(df)

    def singleMarket(self):
        if self.base_currency is None or self.quote_currency is None:
            raise Exception(f"Market not selected base currency is {self.base_currency}\
and quote currency {self.quote_currency}")
        # Specify the base and quote currencies to get single market data
        request_url = f'{self.api_url}/{self.base_currency}/{self.quote_currency}'
        df = pd.DataFrame(requests.get(request_url).json())
        print(df['result'])

    def getHistoricalData(self):
        if self.base_currency is None or self.quote_currency is None:
            raise Exception(f"Market not selected base currency is {self.base_currency}\
and quote currency {self.quote_currency}")
        # Specify the base and quote currencies to get single market data
        request_url = f'{self.api_url}/{self.base_currency}/{self.quote_currency}'
        # 1 day = 60 * 60 * 24 seconds
        daily=str(60*60*24)
        # Start date = 2021-01-01
        start_date = datetime(2021, 1, 1).timestamp()
        # Get the historical market data as JSON
        historical = requests.get(
            f'{request_url}/candles?resolution={daily}&start_time={start_date}'
        ).json()
        # Convert JSON to Pandas DataFrame
        df = pd.DataFrame(historical['result'])
        # Convert time to date
        df['date'] = pd.to_datetime(
            df['time']/1000, unit='s', origin='unix'
        ) 
        # Remove unnecessar columns
        df.drop(['startTime', 'time'], axis=1, inplace=True)
        
        fig = go.Figure()
        fig.update_layout(
            title={
                'text': f"{self.base_currency}/{self.quote_currency}",
                'x':0.5,
                'xanchor': 'center'
            },
            xaxis_title="Date",
            yaxis_title="Price",
            xaxis_rangeslider_visible=False
        )
        fig.add_trace(
            go.Candlestick(
                x=df['date'],
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
        if self.base_currency is None or self.quote_currency is None:
            raise Exception(f"Market not selected. \"base_currency\" is {self.base_currency}\
and \"quote_currency\" is {self.quote_currency}")
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
        if self.base_currency is None or self.quote_currency is None:
            raise Exception(f"Market not selected. \"base_currency\" is {self.base_currency}\
and \"quote_currency\" is {self.quote_currency}")

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
        if self.base_currency is None or self.quote_currency is None:
            raise Exception(f"Market not selected. \"base_currency\" is {self.base_currency}\
and \"quote_currency\" is {self.quote_currency}")
        request_url = f'{self.api_url}/{self.base_currency}/{self.quote_currency}'
        market = requests.get(request_url).json()
        market_ask = market['result']['ask']
        print(f"{self.base_currency}/{self.quote_currency} asking price = {market_ask}")
        return market_ask