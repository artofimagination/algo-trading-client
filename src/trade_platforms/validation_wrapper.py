from typing import List

from trade_platforms.platform_wrapper_base import PlatformWrapper


## Validation platform client wrapper.
#  Gets all the data from the actual platform, but the actions
#  are simulated in this class.
class ValidationWrapper(PlatformWrapper):
    def __init__(self):
        super(ValidationWrapper, self).__init__("ValidationWrapper")

    def placeOrder(self, side, price, volume):
        return None

    def cancelOrder(self, order):
        pass

    def marketAsk(self):
        pass

    def get_order_history(self, side, order_type, start_time, end_time) -> List[dict]:
        return None

    def evaluate(self):
        return (True, None, None)
