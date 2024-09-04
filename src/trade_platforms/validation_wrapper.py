from typing import List
import pandas as pd
import sys
import decimal

decimal.getcontext().prec = 6

from trade_platforms.platform_wrapper_base import PlatformWrapper
from trade_platforms.binance_wrapper import Binance


def truncate(value):
    return int(value * 10000000) / 10000000


## Validation platform client wrapper.
#  Gets all the data from the actual platform, but the actions
#  are simulated in this class.
class ValidationWrapper(PlatformWrapper):
    def __init__(self, platforms, name="ValidationWrapper"):
        super(ValidationWrapper, self).__init__(name)
        # List of real platforms the validation shall happen on.
        self.platform = None
        if platforms is not None:
            self.platform = list(platforms.values())[0]

        self.USD = 'USDT'

        ## Current datast element data of the processing.
        self.current_data = None

        # ---------- Balances
        ## Simulated balance data.
        self.balances = None
        self.order_placed = False

        # ---------- Orders
        ## Stores the highest order price ever made. Needed optimize order search
        self.highest_order_price = 0
        ## Stores the lowest order price ever made. Needed optimize order search
        self.lowest_order_price = sys.maxsize
        self.orders_of_interest = None
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
        self.orders.set_index('price')
        ## Order id watermark.
        self.order_id_watermark = 0

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
            "takerFee": 0.07 / 100.0,
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

    ## Sets the inital test balance in quote currency.
    #  @param balance Amount of the initial balance
    def set_start_balance(self, balance):
        self.balances = {
            self.USD: {
                "coin": self.USD,
                "free": balance,
                "spotBorrow": 0.0,
                "total": balance,
                "usdValue": balance,
                "availableWithoutBorrow": balance
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

    ## Returns the simulation start timestamp.
    def get_start_timestamp(self):
        return self.start_time

    ## Calculates the amounts and stores the order in the orders data frame.
    def place_order(self, type, side, price, volume):
        if type == 'market' and price != self.get_current_price():
            print('You defined a price different from the market value in a \'market\' order.\n\
The price will be replaced with market value')
            price = self.get_current_price()

        amount_in_usd = truncate(volume * price)
        if amount_in_usd == 0:
            return None
        if side == 'buy' and self.balances[self.USD]['free'] < amount_in_usd:
            return None
        elif side == 'buy' and self.balances[self.USD]['free'] >= amount_in_usd:
            self.balances[self.USD]['free'] -= amount_in_usd
            self.balances[self.USD]['free'] = truncate(self.balances[self.USD]['free'])
        elif side == 'sell' and self.balances['BTC']['free'] < volume:
            return None
        elif side == 'sell' and self.balances['BTC']['free'] >= volume:
            self.balances['BTC']['free'] -= volume
            self.balances['BTC']['free'] = truncate(self.balances['BTC']['free'])

        if price > self.highest_order_price:
            self.highest_order_price = price
        if price < self.lowest_order_price:
            self.lowest_order_price = price

        self.order_placed = True
        new_order = pd.json_normalize({
            "avgFillPrice": 0,
            "clientId": None,
            "createdAt": self.get_cycle_timestamp(),
            "filledSize": 0.000,
            "future": "BTC-USD",
            "id": self.order_id_watermark,
            "ioc": False,
            "market": "BTC-USD",
            "postOnly": False,
            "price": price,
            "reduceOnly": False,
            "remainingSize": volume,
            "side": side,
            "size": volume,
            "status": "open",
            "type": type
        })
        self.orders = pd.concat([self.orders, new_order])

        response = {"id": self.order_id_watermark}
        self.order_id_watermark += 1
        return response

    ## Cancels the simulated order
    def cancel_order(self, order):
        pass

    ## Returns the current price.
    def fetch_current_price(self):
        return self.platform.fetch_current_price()

    ## Returns the current orderbook.
    def fetch_orderbook(self, depth):
        return self.platform.fetch_orderbook(depth)

    ## Returns the account info.
    def get_account_info(self) -> dict:
        return self.account_info

    def historical_data(self, start_time, end_time, resolution_sec):
        return self.platform.historical_data(start_time, end_time, resolution_sec)

    ## Returns the balances.
    def get_balances(self):
        return self.balances

    def get_order(self, order_id):
        return self.orders[self.orders['id'] == order_id]

    def get_order_history(
            self,
            side: str = None,
            order_type: str = None,
            start_time: float = None,
            end_time: float = None) -> List[dict]:
        """
            Returns the full order history
            TODO: Implement filters.
            Note: for performance purposes, all closed orders are thrown away
            They are not retainable when calling the function.
        """
        return self.orders

    ## Executes a buy order by updating the appropriate wallet values.
    def _execute_buy(self, price, volume):
        received_amount_btc = (volume - volume * self.account_info['takerFee'])
        amount_to_pay = volume * price
        self.balances[self.USD]['total'] -= amount_to_pay
        self.balances[self.USD]['usdValue'] = self.balances[self.USD]['total']
        self.balances['BTC']['total'] += received_amount_btc
        self.balances['BTC']['free'] += received_amount_btc
        self.balances[self.USD]['total'] = truncate(self.balances[self.USD]['total'])
        self.balances['BTC']['total'] = truncate(self.balances['BTC']['total'])
        self.balances['BTC']['free'] = truncate(self.balances['BTC']['free'])
        self.balances['BTC']['usdValue'] = self.balances['BTC']['total'] * price

    ## Executes a sell order by updating the appropriate wallet values.
    def _execute_sell(self, price, volume):
        amount_earned_usd = (volume - volume * self.account_info['takerFee']) * price
        self.balances[self.USD]['total'] += amount_earned_usd
        self.balances[self.USD]['free'] += amount_earned_usd
        self.balances[self.USD]['total'] = truncate(self.balances[self.USD]['total'])
        self.balances[self.USD]['free'] = truncate(self.balances[self.USD]['free'])
        self.balances[self.USD]['usdValue'] = self.balances[self.USD]['total']
        self.balances['BTC']['total'] -= volume
        self.balances['BTC']['total'] = (self.balances['BTC']['total'])
        self.balances['BTC']['usdValue'] = self.balances['BTC']['total'] * price

    ## Updates the order after succesfull sell or buy.
    def _update_order(self, order, volume):
        order['filledSize'] += volume
        order['remainingSize'] -= volume

        # Order is completed.
        if order['remainingSize'] == 0.0:
            order['status'] = 'closed'

        # make sure the calculations are correct and we never get this faulty case.
        if order['filledSize'] + order['remainingSize'] > order['size']:
            raise Exception("Invalid filledSize and/or remainingSize")
        return order

    ## Executes action on a single market order.
    def _execute_market_action(self, order, orderbook, _execute_order):
        for _, orderbook_item in orderbook.iterrows():
            volume = orderbook_item['volume']
            if volume > order['remainingSize']:
                volume = order['remainingSize']
            _execute_order(orderbook_item['price'], volume)
            order = self._update_order(order, volume)
            if order['status'] == 'closed':
                break
        return order

    ## Executes action on a single limit order.
    def _execute_limit_action(self, order, orderbook, _execute_order):
        orderbook_item = \
            orderbook[orderbook['price'] == round(order['price'])]

        # No appropriate market ask/bid found in the orderbook.
        if len(orderbook_item['volume']) == 0:
            return order

        volume = orderbook_item['volume'].iloc[0]
        if volume > order['remainingSize']:
            volume = order['remainingSize']
        _execute_order(order['price'], volume)
        return self._update_order(order, volume)

    ## Checks the order side of a market order and executes the appropriate action
    #  this can be either a sell or buy.
    def _execute_market(self, order):
        if order['side'] == 'buy':
            orderbook = \
                self.current_asks[self.current_asks['price'] >= order['price']]
            return self._execute_market_action(
                order, orderbook, self._execute_buy)
        else:
            orderbook = \
                self.current_bids[self.current_bids['price'] <= order['price']]
            return self._execute_market_action(
                order, orderbook, self._execute_sell)

    ## Checks the order side of a limit order and executes the appropriate action
    #  this can be either a sell or buy.
    def _execute_limit(self, order):
        if order['side'] == 'buy':
            return self._execute_limit_action(
                order, self.current_asks, self._execute_buy)
        else:
            return self._execute_limit_action(
                order, self.current_bids, self._execute_sell)

    ## Run through all orders and execute buy or sell if conditions are met.
    def evaluate_orders(self):
        # Skip execution if none of the order prices are within range.
        if self.get_current_price() >= self.lowest_order_price and \
                self.get_current_price() <= self.highest_order_price:
            self.orders_of_interest_market = self.orders[self.orders['type'] == 'market']
            self.orders_of_interest_market = \
                self.orders_of_interest_market.apply(self._execute_market, axis=1)
            self.orders_of_interest_limit = \
                self.orders[self.orders['type'] == 'limit']
            self.orders_of_interest_limit = \
                self.orders_of_interest_limit.apply(self._execute_limit, axis=1)
            open_market_orders = \
                self.orders_of_interest_market[
                    self.orders_of_interest_market['status'] != 'closed']
            open_limit_orders = \
                self.orders_of_interest_limit[
                    self.orders_of_interest_limit['status'] != 'closed']
            self.orders = open_market_orders
            self.orders = self.orders.append(open_limit_orders)

    def evaluate(self, trade):
        """Evaluates validation tasks."""
        (running, now) = super().evaluate(trade)
        self.balances['BTC']['usdValue'] = \
            self.balances['BTC']['total'] * self.get_current_price()
        self.evaluate_orders()
        return (running, now)

    ## Cleanup at the end of the main loop.
    #  This shall always be the last call in the main loop.
    def cleanup_iteration(self):
        pass
