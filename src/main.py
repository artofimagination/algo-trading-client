from trade_platforms.ftx_wrapper import FTX
from trade_platforms.platform_wrapper_base import Platforms
from dataset_generator import generate_candle_historical_dataset
from bots.hello_bot import HelloBot
from bots.bot_base import Mode

from datetime import datetime


def run_hello_bot():
    platform = {
        'platform_type': Platforms.FTX,
        'base_currency': 'BTC',
        'quote_currency': 'USD'
    }
    dataset_file = generate_candle_historical_dataset(
        platform=platform,
        start_time=datetime(2020, 1, 1),
        end_time=datetime(2022, 1, 1),
        resolution_sec=15)

    bot = HelloBot(platforms=[
        FTX(base_currency="BTC", quote_currency="USD")
    ],
        mode=Mode.Test)

    if bot.mode == Mode.Test:
        bot.set_test_data_interval(
            test_data_location=dataset_file,
            start_time=datetime(2021, 1, 1, 0, 0),
            end_time=datetime(2021, 1, 1, 3, 0)
        )
    if bot.mode != Mode.Production:
        bot.set_start_balance(200)
    bot.set_wait_time(wait_time_seconds=12)
    bot.run()


if __name__ == "__main__":
    run_hello_bot()
    print("Exiting application...")
