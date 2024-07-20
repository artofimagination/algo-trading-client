import logging
import os
from dotenv import load_dotenv
import pandas as pd
from datetime import timedelta
from typing import List

from base64 import b64encode
from Crypto.Hash import SHA256
from Crypto.PublicKey import RSA
from Crypto.Signature import pkcs1_15

from binance.spot import Spot as Client
from binance.lib.utils import config_logging
from trade_platforms.platform_wrapper_base import PlatformWrapper

config_logging(logging, logging.DEBUG)


class Binance(PlatformWrapper):
    OPENING_TIME_NAME = 0

    def __init__(self, base_currency, quote_currency):
        super(Binance, self).__init__(f'Binance-{base_currency}-{quote_currency}')
        self.api_url = 'https://api1.binance.com'
        self.testnet = False
        # Load env to get API key
        load_dotenv()
        self.api_key = os.getenv("BINANCE_API_KEY")
        self.api_secret = os.getenv("BINANCE_API_SECRET")
        self.base_currency = base_currency
        self.quote_currency = quote_currency
        if base_currency is None or quote_currency is None:
            self.symbol = None
        else:
            self.symbol = base_currency + quote_currency

    def client(self, key, secret, base_url):
        if self.testnet:
            return ClientTestNet(key, secret, base_url=base_url)
        else:
            return Client(key, secret, base_url=base_url)

    def get_account_info(self):
        client = self.client(self.api_key, self.api_secret, base_url=self.api_url)
        return client.account(recvWindow=6000)

    def get_order_history(self, start_time):
        client = self.client(self.api_key, self.api_secret, base_url=self.api_url)
        return client.get_orders(self.symbol, startTime=int(start_time * 1000))

    def get_order(self, order_id):
        client = self.client(self.api_key, self.api_secret, base_url=self.api_url)
        return pd.DataFrame(client.get_order(self.symbol, order_id))

    def exchange_info(self):
        client = self.client(self.api_key, self.api_secret, base_url=self.api_url)
        return pd.DataFrame(client.exchange_info()['symbols'])

    def fetch_orderbook(self, limit):
        client = self.client(self.api_key, self.api_secret, base_url=self.api_url)
        orderbook = client.depth(self.symbol, limit=limit)
        orderbook_bids = pd.DataFrame(orderbook['bids'])
        orderbook_asks = pd.DataFrame(orderbook['asks'])
        orderbook_bids.columns = ['price', 'volume']
        orderbook_asks.columns = ['price', 'volume']
        orderbook_bids.sort_values(by='price', ascending=False)
        return (orderbook_bids, orderbook_asks)

    ## Get historical data
    #  @param start_date starting date of the data
    #  @param end_date end date of the data
    #  @param resolution of the data
    def historical_data(
            self, start_time, end_time, resolution="15m", limit=1000):
        # Specify the base and quote currencies to get single market data
        client = self.client(self.api_key, self.api_secret, base_url=self.api_url)
        if start_time is None:
            candles = client.klines(
                self.symbol,
                resolution,
                limit=limit)
        elif end_time is None:
            candles = client.klines(
                self.symbol,
                resolution,
                startTime=int(start_time * 1000),
                limit=limit)
        else:
            candles = client.klines(
                self.symbol,
                resolution,
                startTime=int(start_time * 1000),
                endTime=int(end_time * 1000),
                limit=limit)
        if 'msg' in candles and candles['msg'] == "Invalid symbol.":
            return None

        # Convert JSON to Pandas DataFrame
        df = pd.DataFrame(candles)
        if len(df) == 0:
            return df
        df.iloc[:, 1] = pd.to_numeric(df.iloc[:, 1])
        df.iloc[:, 2] = pd.to_numeric(df.iloc[:, 2])
        df.iloc[:, 3] = pd.to_numeric(df.iloc[:, 3])
        df.iloc[:, 4] = pd.to_numeric(df.iloc[:, 4])
        df.iloc[:, 5] = pd.to_numeric(df.iloc[:, 5])
        df.iloc[:, 7] = pd.to_numeric(df.iloc[:, 7])
        df.iloc[:, 9] = pd.to_numeric(df.iloc[:, 9])
        df.iloc[:, 10] = pd.to_numeric(df.iloc[:, 10])
        df.iloc[:, 11] = pd.to_numeric(df.iloc[:, 11])
        cols_ = list()
        cols_.append('startTime')
        cols_.append('open')
        cols_.append('high')
        cols_.append('low')
        cols_.append('close')
        cols_.append('volume')
        cols_.append('closeTime')
        cols_.append('quoteAssetVolume')
        cols_.append('noOfTrades')
        cols_.append('takerByBaseAssetVol')
        cols_.append('takerByQuoteAssetVol')
        cols_.append('ignore')
        df.columns = cols_
        df['startTime'] = pd.to_datetime(df['startTime'], unit='ms')
        # Ensure all numeric columns are of type float
        df['open'] = df['open'].astype(float)
        df['high'] = df['high'].astype(float)
        df['low'] = df['low'].astype(float)
        df['close'] = df['close'].astype(float)
        df['volume'] = df['volume'].astype(float)
        df['closeTime'] = pd.to_datetime(df['closeTime'], unit='ms')
        df['quoteAssetVolume'] = df['quoteAssetVolume'].astype(float)
        df['noOfTrades'] = df['noOfTrades'].astype(int)
        df['takerByBaseAssetVol'] = df['takerByBaseAssetVol'].astype(float)
        df['takerByQuoteAssetVol'] = df['takerByQuoteAssetVol'].astype(float)
        df['ignore'] = df['ignore'].astype(int)
        return df

    def fetch_price(self, datetime):
        df = self.historical_data(
            datetime, datetime + timedelta(seconds=15).timestamp(), "1m", 1)
        if len(df) > 0:
            return df['open'].values[0]
        else:
            print("No price returned...")
            return 0

    ## Returns all wallet balances.
    def get_balances(self):
        account = self.get_account_info()
        return account['balances']

    ## Gets the current price from the platform wrapper.
    def fetch_current_price(self):
        client = self.client(self.api_key, self.api_secret, base_url=self.api_url)
        return client.ticker_price(self.symbol)['price']


class BinanceTestNet(Binance):
    def __init__(self, base_currency, quote_currency):
        super(BinanceTestNet, self).__init__(base_currency, quote_currency)
        self.testnet = True
        self.api_url = 'https://testnet.binance.vision'
        self.api_key = os.getenv("BINANCE_TESTNET_API_KEY")
        self.api_secret = None


class ClientTestNet(Client):
    def __init__(self, key=None, secret=None, **kwargs):
        super(ClientTestNet, self).__init__(key, secret, **kwargs)

    def _get_sign(self, data):
        # load private key
        with open('/workspaces/algo-trading-client/test-prv-key.pem', 'r') as f:
            private_key = RSA.import_key(f.read())

        # hash the message
        digest = SHA256.new(data.encode())

        # sign the digest
        return b64encode(pkcs1_15.new(private_key).sign(digest))
