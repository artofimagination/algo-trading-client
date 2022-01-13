from typing import List
import uuid
import pandas as pd

from trade_platforms.platform_wrapper_base import PlatformWrapper


## Validation platform client wrapper.
#  Gets all the data from the actual platform, but the actions
#  are simulated in this class.
class ValidationWrapper(PlatformWrapper):
    def __init__(self, name="ValidationWrapper"):
        super(ValidationWrapper, self).__init__(name)
        ## Simulated balance value in USD
        self.start_balance_USD = 200
        ## Simulated balance data
        self.balances = {
            "USD": {
                "coin": "USD",
                "free": self.start_balance_USD,
                "spotBorrow": 0.0,
                "total": self.start_balance_USD,
                "usdValue": self.start_balance_USD,
                "availableWithoutBorrow": self.start_balance_USD
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

        ## Simulated order history data frame
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

    ## Sets the inital test balance in USD.
    def set_start_balance(self, balance_USD):
        self.start_balance_USD = balance_USD

    ## Calculates the amounts and stores the order in the orders data frame.
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

    ## Cancels the simulated order
    def cancelOrder(self, order):
        pass

    ## Returns the current market ask.
    def marketAsk(self):
        pass

    ## Returns the account info.
    def get_account_info(self):
        return self.account_info

    ## Returns the balances.
    def get_balances(self):
        return self.balances

    ## Returns the full order history
    # TODO: Implement filters.
    def get_order_history(
            self,
            side: str = None,
            order_type: str = None,
            start_time: float = None,
            end_time: float = None) -> List[dict]:
        return self.orders

    ## Executes a buy order.
    def _execute_buy(self, price, volume):
        amount_to_pay = (volume + volume * self.account_info['takerFee']) * price
        self.balances['USD']['total'] -= amount_to_pay
        self.balances['USD']['usdValue'] = self.balances['USD']['total']
        self.balances['BTC']['total'] += volume
        self.balances['BTC']['free'] += volume
        self.balances['BTC']['usdValue'] = self.balances['BTC']['total'] * price

    ## Executes a sell order.
    def _execute_sell(self, price, volume):
        amount_to_earn = (volume - volume * self.account_info['takerFee']) * price
        self.balances['USD']['total'] += amount_to_earn
        self.balances['USD']['free'] += amount_to_earn
        self.balances['USD']['usdValue'] = self.balances['USD']['total']
        self.balances['BTC']['total'] -= volume
        self.balances['BTC']['usdValue'] = self.balances['BTC']['total'] * price

    ## Execute all orders.
    #  This is called on every item of the orders dataframe.
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

    ## Evaluates validation tasks.
    def evaluate(self):
        self.orders = self.orders.apply(self._execute_orders, axis=1)
        return (True, None, None)

    ## Cleanup at the end of the main loop.
    #  This shall always be the last call in the main loop.
    def cleanup_iteration(self):
        self.orders = self.orders[self.orders.status != 'closed']
