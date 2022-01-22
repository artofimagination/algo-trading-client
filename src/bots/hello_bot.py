from bots.bot_base import Mode, BotBase

from random import random


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
    def _trade(self, df):
        market_value = df['market']
        current_balances = self.get_balances()
        amount_to_trade_USD = current_balances / 10
        market_structure = self._determine_market_structure(df)
        if market_structure == 'bullish':
            price = market_value + 100
            order_result = self.place_order(
                side='buy', price=price, volume=amount_to_trade_USD / market_value)
        elif market_structure == 'bearish':
            price = market_value - 100
            order_result = self.place_order(
                side='sell', price=price, volume=amount_to_trade_USD / market_value)

        if order_result is None:
            print('Order failed. Balance has not enough free amount')

    # Load your test data set or any local variables, members if needed.
    def _setup(self):
        # Setup the main loop with an initial evaluation.
        (running, timestamp) = self.evaluate(self._trade)
        # Optional: Setup plot data
        self.init_plot_data()

    ## Main loop of the algorithm
    def run(self):
        try:
            self._setup()
            # Main loop of the algorithm
            while True:
                ##########################
                # Each iteration the platform will evaluate tasks
                # (For example getting the current test data,
                # or getting current market, in production mode).
                # Custom trading logic, put your decision making within _trade()
                (running, _, timestamp) = self.evaluate(self._trade)
                if not running:
                    break
                ##########################

                ##########################
                # Optional: statistical data for plotting in a
                # configurable window of interest.
                # Following data can be displayed:
                # Balance in case the inital balance was traded
                # once at the beginning then traded back at the end
                # BalanceIfTradedOnce = 0x0001
                # Start balance
                # StartBalance = 0x0002
                # Cumulative quote currency value of all wallets
                # BalanceCumulative = 0x0004
                # Quote currency wallet total
                # QuoteCurrencyTotal = 0x0008
                # Quote currency traded amount within time window
                # QuoteCurrencyInTimeWindow = 0x0010
                # Quote currency free amount
                # QuoteCurrencyFree = 0x0020
                # Base currency traded amount within time window
                # BaseCurrencyBalanceInWindow = 0x0040
                # Base currency total amount.
                # BaseCurrencyTotal = 0x0080
                # Base currency free amount.
                # BaseCurrencyFree = 0x0100
                # Candle price history
                # Candles = 0x0200
                self.accumulate_plot_data(timestamp, window_of_interest_seconds=15)
                ##########################

                ##########################
                # Doing platform client related cleanup if there is any.
                # Always keep this at the end of the loop, like in this example
                self.cleanup_iteration()
                ##########################
        except KeyboardInterrupt:
            pass
        # Optional: Once the simulation loop is done
        # Plot the accumulated data.
        self.plot_data(timestamp)
