from trade_platforms.ftx_wrapper import FTX
from bots.hello_bot import HelloBot
from bots.bot_base import Mode

from datetime import datetime

if __name__ == "__main__":
    bot = HelloBot(platforms=[
        FTX(base_currency="BTC", quote_currency="USD")
    ],
    bot.set_test_data_interval(
        start_time=datetime(2021, 2, 1, 0, 0),
        end_time=datetime(2021, 2, 2, 0, 0)
    )
    bot.set_start_balance(200)
    bot.run()
    print("Exiting application...")
