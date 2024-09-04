from PyQt5.QtCore import QObject, QThread
from PyQt5 import QtCore

import traceback
import sys
from datetime import datetime

from trade_platforms.binance_wrapper import Binance
from trade_platforms.platform_wrapper_base import Platforms
from dataset_generator import generate_candle_historical_dataset
from bots.hello_bot import HelloBot
from bots.bot_base import Mode

BOT_HELLO = "Hello Bot"
BOT_INTUITION = "Intuition Bot"


# Signals used by the backend.
class BackendSignals(QtCore.QObject):
    finished = QtCore.pyqtSignal()
    error = QtCore.pyqtSignal(tuple)
    run_completed = QtCore.pyqtSignal()


class Backend(QObject):
    """ Backend logic to handle UI data generation and trading algorithm.
    """

    def __init__(self):
        super(Backend, self).__init__()
        self.signals = BackendSignals()
        self.bot = None

        # Thread break guard condition, when true the thread finishes.
        self.stop = False

    def run_hello_bot(self):
        """Runs the HelloBot on binance test data"""
        simulation_start = datetime(2020, 1, 1, 0, 0)
        simulation_end = datetime(2020, 1, 1, 1, 0)
        platform = {
            'platform_type': Platforms.Binance,
            'base_currency': 'BTC',
            'quote_currency': 'USDT'
        }
        dataset_file = generate_candle_historical_dataset(
            platform=platform,
            start_time=simulation_start,
            end_time=simulation_end,
            resolution_sec=60)

        self.bot = HelloBot(platforms=[
            Binance(base_currency="BTC", quote_currency="USDT")
        ],
            mode=Mode.Test,
            resolution_sec=60)

        if self.bot.mode == Mode.Test:
            self.bot.set_test_data_interval(
                test_data_location=dataset_file,
                start_time=simulation_start,
                end_time=simulation_end
            )
        if self.bot.mode != Mode.Production:
            self.bot.set_start_balance(200)
        self.bot.set_wait_time(wait_time_seconds=0)
        self.bot.run()

    def download(self):
        """Downloads the data hardcoded in this function"""
        simulation_start = datetime(2023, 1, 1, 0, 0)
        simulation_end = datetime(2024, 1, 1, 0, 0)
        resolution_sec = 1
        platform = {
            'platform_type': Platforms.Binance,
            'base_currency': 'BTC',
            'quote_currency': 'USDT'
        }
        generate_candle_historical_dataset(
            platform=platform,
            start_time=simulation_start,
            end_time=simulation_end,
            resolution_sec=resolution_sec)

    def run_bot(self, selected_bot: str):
        """Runs the selected bot"""
        if selected_bot == BOT_HELLO:
            self.run_hello_bot()
        elif selected_bot == BOT_INTUITION:
            self.run_intuition_bot()
        self.signals.run_completed.emit()

    @QtCore.pyqtSlot()
    def run(self):
        try:
            print("Backend")
            while (True):
                if self.stop:
                    break

                QThread.msleep(10)

        except Exception:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        finally:
            self.signals.finished.emit()  # Done
