from enum import Enum

from trade_platforms.ftx_wrapper import FTX

class Platform(Enum):
    FTX = 0
    Binance = 1

class Mode(Enum):
    Test = 0
    Validation = 1
    Production = 2

class BotBase():
    def __init__(self, platforms, mode):
        self.platforms = dict()
        for trade_platform in platforms:
            self.platforms[trade_platform.name] = trade_platform
            self.mode = mode

    def _placeOrder(self, platform_name, side, price, volume):
        if platform_name not in self.platforms:
            raise Exception(f"{platform_name} is an unknown platform name")
        return self.platforms[platform_name].placeOrder(side, price, volume)

    def _cancelOrder(self, platform_name, order):
        if platform_name not in self.platforms:
            raise Exception(f"{platform_name} is an unknown platform name")
        self.platforms[platform_name].cancelOrder(order)

    def _marketAsk(self, platform_name):
        if platform_name not in self.platforms:
            raise Exception(f"{platform_name} is an unknown platform name")
        return self.platforms[platform_name].marketAsk()

    def run(self):
        pass
