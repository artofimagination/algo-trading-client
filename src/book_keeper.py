import pandas as pd


class BookKeeper():
    def __init__(self):
        self.orders_tree = pd.DataFrame({
            'order_id': [],
            'timestamp': [],
            'volume': [],
            'price': [],
            'side': [],
            'source_timestamp': [],
            'source_order_id': [],
            'source_price': [],
            'source_side': []
        })
        self.tax_by_transactions = pd.DataFrame({
            'order_id': [],
            'amount': []
        })
        self.total_tax = 0
        self.total_income = 0
        self.total_profit = 0
        self.tax_rate = 0.225
