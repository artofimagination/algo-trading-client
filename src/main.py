from trade_platforms.ftx_wrapper import FTX
from trade_platforms.platform_wrapper_base import Platforms
from dataset_generator import generate_candle_historical_dataset
from bots.hello_bot import HelloBot
from bots.bot_base import Mode

from datetime import datetime


def run_hello_bot():
    simulation_start = datetime(2020, 1, 1, 0, 0)
    simulation_end = datetime(2020, 1, 1, 0, 2)
    platform = {
        'platform_type': Platforms.FTX,
        'base_currency': 'BTC',
        'quote_currency': 'USD'
    }
    dataset_file = generate_candle_historical_dataset(
        platform=platform,
        start_time=simulation_start,
        end_time=simulation_end,
        resolution_sec=15)

    bot = HelloBot(platforms=[
        FTX(base_currency="BTC", quote_currency="USD")
    ],
        mode=Mode.Test)

    if bot.mode == Mode.Test:
        bot.set_test_data_interval(
            test_data_location=dataset_file,
            start_time=simulation_start,
            end_time=simulation_end
        )
    if bot.mode != Mode.Production:
        bot.set_start_balance(200)
    bot.set_wait_time(wait_time_seconds=0)
    bot.run()


if __name__ == "__main__":
    run_hello_bot()
    print("Exiting application...")
