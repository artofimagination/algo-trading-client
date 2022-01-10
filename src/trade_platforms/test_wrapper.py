from typing import List
import uuid
from datetime import datetime, timedelta
import pandas as pd
import plotly.graph_objects as go

from trade_platforms.platform_wrapper_base import PlatformWrapper


## Test platform client wrapper.
#  Simulates platform behavior using pregenerated test data.
#  No connection is used to a real platform.
class TestWrapper(PlatformWrapper):
    def __init__(self):
        super(TestWrapper, self).__init__("TestWrapper")
        # Stores the test data set the wrapper will feed to the bot.
        self.testData = None
        self.start = datetime(2021, 2, 1, 0, 0)
        self.end = datetime(2021, 2, 4, 0, 0)
        self.timestamp = self.start
        self.overall_progress = self.start
        self.chunk_progress = 0
        self.previous_data = None
        self.historical_data = pd.DataFrame({
            "close": [],
            "high": [],
            "low": [],
            "open": [],
            "startTime": [],
            "volume": []
        })
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
        self.start_amount_USD = 200
        self.balances = {
            "USD": {
                "coin": "USD",
                "free": self.start_amount_USD,
                "spotBorrow": 0.0,
                "total": self.start_amount_USD,
                "usdValue": self.start_amount_USD,
                "availableWithoutBorrow": self.start_amount_USD
            },
            "BTC": {
                "coin": "BTC",
                "free": 0.0,
                "spotBorrow": 0.0,
                "total": 0.0,
                "usdValue": 0.0,
                "availableWithoutBorrow": 0.0
            }
        }
        self.orders = pd.DataFrame({
            "avgFillPrice": [],
            "clientId": [],
            "createdAt": [],
            "filledSize": [],
            "future": [],
            "id": [],
            "ioc": [],
            "market": [],
            "postOnly": [],
            "price": [],
            "reduceOnly": [],
            "remainingSize": [],
            "side": [],
            "size": [],
            "status": [],
            "type": []})

    def placeOrder(self, side, price, volume):
        amount_to_pay_usd = (volume + volume * self.account_info['takerFee']) * price
        amount_to_pay_btc = volume
        if side == 'buy' and self.balances['USD']['free'] < amount_to_pay_usd:
            return None
        elif side == 'buy' and self.balances['USD']['free'] >= amount_to_pay_usd:
            self.balances['USD']['free'] -= amount_to_pay_usd
        elif side == 'sell' and self.balances['BTC']['free'] < amount_to_pay_btc:
            return None
        elif side == 'sell' and self.balances['BTC']['free'] >= amount_to_pay_btc:
            self.balances['BTC']['free'] -= amount_to_pay_btc

        orderId = uuid.uuid4()
        new_order = pd.json_normalize({
            "avgFillPrice": 10135.25,
            "clientId": None,
            "createdAt": "2019-06-27T15:24:03.101197+00:00",
            "filledSize": 0.000,
            "future": "BTC-USD",
            "id": str(orderId),
            "ioc": False,
            "market": "BTC-USD",
            "postOnly": False,
            "price": price,
            "reduceOnly": False,
            "remainingSize": volume,
            "side": side,
            "size": volume,
            "status": "open",
            "type": "limit"
        })
        self.orders = self.orders.append(new_order)

        response = {"id": orderId}
        return response

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

    def cancelOrder(self, order):
        pass

    def marketAsk(self):
        pass

    def get_start_timestamp(self):
        return self.start

    def get_account_info(self):
        return self.account_info

    def set_test_data(self, df):
        self.testData = df

    def get_balances(self):
        return self.balances

    def get_order_history(
            self,
            side: str = None,
            order_type: str = None,
            start_time: float = None,
            end_time: float = None) -> List[dict]:
        return self.orders

    def _execute_buy(self, price, volume):
        amount_to_pay = (volume + volume * self.account_info['takerFee']) * price
        self.balances['USD']['total'] -= amount_to_pay
        self.balances['USD']['usdValue'] = self.balances['USD']['total']
        self.balances['BTC']['total'] += volume
        self.balances['BTC']['free'] += volume
        self.balances['BTC']['usdValue'] = self.balances['BTC']['total'] * price

    def _execute_sell(self, price, volume):
        amount_to_earn = (volume - volume * self.account_info['takerFee']) * price
        self.balances['USD']['total'] += amount_to_earn
        self.balances['USD']['free'] += amount_to_earn
        self.balances['USD']['usdValue'] = self.balances['USD']['total']
        self.balances['BTC']['total'] -= volume
        self.balances['BTC']['usdValue'] = self.balances['BTC']['total'] * price

    def _execute_orders(self, order):
        if self.previous_data is not None and \
            ((self.previous_data['open'] >= self.previous_data['close'] and
                order['price'] <= self.previous_data['open'] and
                order['price'] >= self.previous_data['close']) or
                (self.previous_data['open'] < self.previous_data['close'] and
                    order['price'] >= self.previous_data['open'] and
                    order['price'] <= self.previous_data['close'])):
            order['filledSize'] = order['size']
            order['remainingSize'] = 0.0
            order['status'] = 'closed'
            if order['side'] == 'buy':
                self._execute_buy(order['price'], order['size'])
            else:
                self._execute_sell(order['price'], order['size'])
        return order

    def evaluate(self):
        if self.overall_progress > self.end:
            return (False, None, None)

        percentage = ((self.overall_progress - self.start) /
                      (self.end - self.start)) * 100
        print(f"{percentage:.3f}%")
        timestamp = self.timestamp
        chunk_length = len(self.testData[timestamp.strftime("DF%Y%m%d")])
        self.orders = self.orders.apply(self._execute_orders, axis=1)

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

    def cleanup_iteration(self):
        self.orders = self.orders[self.orders.status != 'closed']
