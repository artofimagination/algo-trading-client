from bots.bot_base import Mode, BotBase

from datetime import timedelta
from random import random

## This is a tutorial bot, to create and run an instance run the following
#  The code bellow will create a HelloBot, that has an FTX client on the BTC USB market
#
#    bot = HelloBot(platforms=[
#        FTX(base_currency="BTC", quote_currency="USD")
#    ],
#    mode=Mode.Test)
#    bot.run()


## Exmaple trade bot for tutorial purposes.
# It is suggested to use, the following basic structure
# when writing your own bot.
class HelloBot(BotBase):
    ## When creating your custom bot, just copy this over and rename
    # to your desired name
    def __init__(self, platforms, mode=Mode.Test):
        super(HelloBot, self).__init__(platforms, mode)

    ## Implement your way of market structure detector
    # This example decide purely randomly.
    def _determine_market_structure(self):
        rand = random()
        if rand > 0.5:
            return 'bullish'
        return 'bearish'

    ## This function should do the main trading logic.
    def _trading(self, df):
        market_value = df['market']
        current_balances = self.get_balances()
        amount_to_trade_USD = current_balances / 10
        market_structure = self._determine_market_structure(df)
        if market_structure == 'bullish':
            price = market_value + 100
            order_result = self.placeOrder(
                side='buy', price=price, volume=amount_to_trade_USD / market_value)
        elif market_structure == 'bearish':
            price = market_value - 100
            order_result = self.placeOrder(
                side='sell', price=price, volume=amount_to_trade_USD / market_value)

        if order_result is None:
            print('Order failed. Balance has not enough free amount')

    # Load your test data set or any local variables, members if needed.
    def _setup(self):
        pass

    ## Main loop of the algorithm
    def run(self):
        self._setup()

        # Get start timestamp, useful for calculating timing
        previous_timestamp = self.get_start_timestamp()
        # Main loop of the algorithm
        while True:
            ##########################
            # Each iteration the platform will evaluate tasks
            # (For example getting the current test data,
            # or getting current market, in production mode).
            (running, df, timestamp) = self.evaluate()
            if not running:
                break
            ##########################

            ##########################
            # Custom trading logic, put your decision making within _trading()
            self._trade(df)
            ##########################

            ##########################
            # Statistical data for plotting and profiling in a configurable
            # time window (60 minutes in this example).
            if (timestamp - previous_timestamp >= timedelta(minutes=60)):
                pass
            ##########################

            ##########################
            # Doing platform client related cleanup if there is any.
            # Always keep this at the end of the loop, like in this example
            self.cleanup_iteration()
            ##########################
