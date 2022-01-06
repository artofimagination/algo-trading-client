from bots.bot_base import Mode, BotBase

## Exmaple trade bot for tutorial purposes.
class HelloBot(BotBase):
    ## When creating your custom bot, just copy this over and rename
    # to your desired name
    def __init__(self, platforms, mode = Mode.Test):
        super(HelloBot, self).__init__(platforms, mode)

    ## Main loop of the algorithm
    def run(self):
        market_ask = self._marketAsk("FTX BTCUSD")
        order_result = self._placeOrder(platform_name="FTX BTCUSD", side="buy", price=market_ask * 0.9, volume=0.0001)
        self._cancelOrder(platform_name="FTX BTCUSD", order=order_result)

