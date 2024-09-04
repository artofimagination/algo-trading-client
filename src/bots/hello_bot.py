from bots.bot_base import Mode, BotBase, PlotOptions
import pandas as pd
from datetime import timedelta


class HelloBot(BotBase):
    """
        Example trade bot for tutorial purposes. It is suggested to use the following basic structure
        when writing your own bot. When creating your custom bot, just copy this over and rename the class
        to your desired name.
    """
    def __init__(self, platforms, mode=Mode.Test, resolution_sec=60):
        super(HelloBot, self).__init__(platforms, mode, resolution_sec)
        self.count = 0
        # Arbitrary structure to show order visualization.
        self.completed_orders = pd.DataFrame({
            'order_id': [],
            'expiry_length': [],
            'status': [],
            'age': [],
            'timestamp': [],
            'exec_timestamp': [],
            'volume': [],
            'volume_USD': [],
            'price': [],
            'start_price': [],
            'side': [],
        })

        self.order_id_watermark = 0

    def _determine_bias(self):
        """
            Implement your way of market bias detector
            This example will switch bias every cycle.
        """
        self.count += 1
        if self.count % 2 == 1:
            return 'bullish'
        return 'bearish'

    def _trade(self):
        """This function should do the main trading logic."""
        market_value = self.get_current_price()
        current_balance = self.get_balances()['USDT']['total']
        amount_to_trade_USD = current_balance / 10
        market_structure = self._determine_bias()
        if market_structure == 'bullish':
            order_result = self.place_order(
                type='market',
                side='sell',
                price=market_value,
                volume=amount_to_trade_USD / market_value)
        elif market_structure == 'bearish':
            order_result = self.place_order(
                type='market',
                side='buy',
                price=market_value,
                volume=amount_to_trade_USD / market_value)
            if order_result is not None:
                # Example order added to the list, so we can draw it on the candle chart.
                new_order = pd.json_normalize({
                    'order_id': self.order_id_watermark,
                    'age': 0,
                    'timestamp': self.get_cycle_timestamp(),
                    'exec_timestamp': self.get_cycle_timestamp() + timedelta(seconds=420),
                    'volume': amount_to_trade_USD / market_value,
                    'volume_USD': amount_to_trade_USD,
                    'price': 7188,
                    'start_price': 7184,
                    'side': 'buy',
                })
                self.completed_orders = pd.concat([self.completed_orders, new_order])
            else:
                # Order failed. Balance has not enough free amount'
                pass
        return True

    def _setup(self):
        """Load your test data set or any local variables, members if needed."""
        self.count = 0
        # Setup the main loop with an initial evaluation.
        (running, timestamp) = self.evaluate(self._trade)
        # Optional: Setup plot data
        self.init_plot_data()

    def run(self):
        """Main loop of the algorithm."""
        try:
            self._setup()
            # Main loop of the algorithm
            while True:
                ##########################
                # Each iteration the platform will evaluate tasks
                # (For example getting the current test data,
                # or getting current market, in production mode).
                # Custom trading logic, put your decision making within _trade()
                (running, timestamp) = self.evaluate(self._trade)
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
        self.plot_data(timestamp, PlotOptions.USDPlot.value | PlotOptions.BTCPlot.value | PlotOptions.Candles.value)
