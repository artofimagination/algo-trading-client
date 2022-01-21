from plotly.subplots import make_subplots
from bots.bot_base import Mode, BotBase

import pandas as pd
from os.path import exists
from datetime import datetime, timedelta
import plotly.express as px
import random
import copy


def plotLineChart(df):
    figures = list()
    figures.append(
        px.line(df, x="day", y="mean_candle_height", title='Candle height mean per day'))
    figures.append(
        px.line(df, x="day", y="mean_price", title='Price mean per day'))
    figures.append(
        px.line(df, x="day", y="count", title='Price change counts', color="group"))
    # For as many traces that exist per Express figure,
    # get the traces from each plot and store them in an array.
    # This is essentially breaking down the Express fig into it's traces
    figureTracesList = list()
    for figure in figures:
        figureTrace = []
        for trace in range(len(figure["data"])):
            figureTrace.append(figure["data"][trace])
        figureTracesList.append(figureTrace)

    fig = make_subplots(rows=3)

    # Get the Express fig broken down as traces
    # and add the traces to the proper plot within in the subplot.
    for i, figureTraces in enumerate(figureTracesList):
        for traces in figureTraces:
            fig.append_trace(traces, row=i + 1, col=1)
    fig.show()


class NaiveBot(BotBase):
    # FTX data set path.
    # From 01-01-2020 to 01-01-2022
    # 1 minute resolution
    # stored in day chunks (ID DFyyyymmdd)
    FTX_DATASET_PATH = 'src/bots/data/candle_\
dataset_ftx_20200101-20220101_minutes_res_day_chunks.h5'

    def __init__(self, platforms, mode=Mode.Test):
        super(NaiveBot, self).__init__(platforms, mode)
        self.BTC_per_window_of_interest = list()
        self.balance_USD_per_window_of_interest = list()
        self.candle_history_accumulator = 0
        self.candle_history = list()

    def run(self):
        self.order_based_on_candle_direction_TEST()

    def train(self):
        if not exists(self.FTX_DATASET_PATH):
            print("Dataset does not exist")
            return
        start = datetime(2020, 1, 1)
        end = datetime(2022, 2, 1)

        timestamp = start
        store = pd.HDFStore(self.FTX_DATASET_PATH)
        output = pd.DataFrame({
                              "day": [],
                              "group": [],
                              "mean_candle_height": [],
                              "mean_price": [],
                              "count": []})

        while timestamp <= end:
            percentage = ((timestamp - start) / (end - start)) * 100
            print(f"{percentage:.2f}%")
            start_date = timestamp
            timestamp += timedelta(minutes=60 * 24)
            conditions = [
                (-50000, -50),
                (-50, -5),
                (-5, -2),
                (-2, 0),
                (0, 2),
                (2, 5),
                (5, 50),
                (50, 50000)]
            df = store[start_date.strftime("DF%Y%m%d")]
            meanHeight = (df['close'] - df['open']).mean()
            meanPrice = (df['close'] + df['open']).mean() / 2.0
            for condition in conditions:
                df_condition = df.apply(lambda x: True
                                        if x['close'] - x['open'] >= condition[0] and
                                        x['close'] - x['open'] < condition[1] else
                                        False, axis=1)
                # Count number of True in the series
                count = len(df_condition[df_condition == True].index)
                output.loc[len(output)] = [
                    start_date,
                    f">= {condition[0]} && < {condition[1]}",
                    meanHeight,
                    meanPrice,
                    count]
        plotLineChart(output)

    # This function generates random order volumes and random BTC price changes.
    # Then does a BTC sale and buy and calculates the gain.
    # It plots then all random generated data in a scatter plot where each dot's color
    # represents which gain range the random order and price change will result.
    # For example selling 58K USD worth of BTC , then buying it after a 40K drop
    # the gain will be in the 1.1 - 2.3 BTC range.
    def plotBTCGain(self, max_price_diff, max_trade_volume, price=60000):
        fee = 0.004
        btcVolume = 1.0
        df = pd.DataFrame({
                          "priceDiffUSD": [],
                          "tradeVolumeUSD": [],
                          "cashoutUSD": [],
                          "finalVolumeBTC": [],
                          "diff_category": []})
        for i in range(0, 10000):
            # Progress of the simulation in %.
            percentage = (i / 10000) * 100
            print(f"{percentage:.2f}%")

            # Randomized BTC priceChange
            priceDiffUSD = random.random() * max_price_diff
            # Randomized order volume USD
            tradeVolumeUSD = random.random() * max_trade_volume
            # Calculate BTC after selling "tradeVolumeUSD" worth of BTC then,
            # buying for "tradeVolumeUSD" after the "priceChange"
            # Also takes into account FTX fees (0.4%)
            btcVolumeNew = btcVolume - (tradeVolumeUSD + tradeVolumeUSD * fee) / price + \
                (tradeVolumeUSD - tradeVolumeUSD * fee) / (price - priceDiffUSD)
            # Original and new balance difference
            diff = btcVolumeNew - btcVolume
            # Amount of cash after selling everything on the original price.
            cashoutUSD = (btcVolumeNew - btcVolumeNew * fee) * price
            # If the volume is negative all is lost.
            if btcVolumeNew < 0:
                cashoutUSD = 0

            category = "misc"
            divider = 2.0
            left = -10
            found = False
            # Calculates and checks which gain range the current gain
            # fits in on the negative side.
            for condition in range(-20, 1):
                divider = divider * 2.0
                right = condition / divider
                if diff >= left and diff < right:
                    category = f">= {left} && < {right}"
                    found = True
                    break
                left = right

            if found:
                df.loc[len(df)] = [
                    priceDiffUSD, tradeVolumeUSD, cashoutUSD, btcVolumeNew, category]
                continue

            divider = 2.0
            right = 10
            # Calculates and checks which gain range the current gain
            # fits in on the positive side.
            for condition in reversed(range(0, 21)):
                divider = divider * 2.0
                left = condition / divider
                if diff >= left and diff < right:
                    category = f">= {left} && < {right}"
                    break
                right = left

            df.loc[len(df)] = [
                priceDiffUSD,
                tradeVolumeUSD,
                cashoutUSD,
                btcVolumeNew,
                category]

        fig = px.scatter(
            df,
            x="priceDiffUSD",
            y="tradeVolumeUSD",
            title='BTC Gain',
            color="diff_category",
            hover_data=['cashoutUSD', 'finalVolumeBTC'])
        fig.show()

    def plotCashoutGain(self, max_trade_volume, max_cashout_price=60000, price=60000):
        fee = 0.004
        btcVolume = 1.0
        df = pd.DataFrame({
            "cashout_priceUSD": [],
            "tradeVolumeUSD": [],
            "cashoutGainUSD": [],
            "diff_category": []})
        for i in range(0, 10000):
            # Progress of the simulation in %.
            percentage = (i / 10000) * 100
            print(f"{percentage:.2f}%")

            cashout_price = price + random.random() * (max_cashout_price - price)
            # Randomized order volume USD
            tradeVolumeUSD = random.random() * max_trade_volume
            # Amount of cash after selling everything on the original price.
            cashoutUSD = (btcVolume - btcVolume * fee) * cashout_price
            cashoutGain = cashoutUSD - price

            category = "misc"
            divider = 1.0
            left = -50000
            found = False
            # Calculates and checks which gain range the current gain
            # fits in on the negative side.
            for _ in range(-10, 1):
                divider = divider * 2.0
                right = left / divider
                if cashoutGain >= left and cashoutGain < right:
                    category = f">= {left} && < {right}"
                    found = True
                    break
                left = right

            if found:
                df.loc[len(df)] = [cashout_price, tradeVolumeUSD, cashoutGain, category]
                continue

            divider = 1.0
            right = 50000
            # Calculates and checks which gain range the current gain
            # fits in on the positive side.
            for _ in reversed(range(0, 11)):
                divider = divider * 2.0
                left = right / divider
                if cashoutGain >= left and cashoutGain < right:
                    category = f">= {left} && < {right}"
                    break
                right = left

            df.loc[len(df)] = [cashout_price, tradeVolumeUSD, cashoutGain, category]

        fig = px.scatter(
            df,
            x="cashout_priceUSD",
            y="tradeVolumeUSD",
            title='Cashout Gain',
            color="diff_category")
        fig.show()

    def _determine_market_structure_based_last_x_candles(self, df):
        diff = 0
        if df['close'] > df['open']:
            diff = 1
        if df['close'] < df['open']:
            diff = -1

        if diff != 0:
            self.candle_history_accumulator += diff
            self.candle_history.append(diff)

        if len(self.candle_history) > 5:
            self.candle_history_accumulator -= self.candle_history[0]
            self.candle_history.pop(0)

        if len(self.candle_history) >= 5:
            if self.candle_history_accumulator > 2.0:
                return 'bullish'
            elif self.candle_history_accumulator < -2.0:
                return 'bearish'
        return 'uncertain'

    def _determine_market_structure_based_on_candle_direction(self, df):
        if df['close'] > df['open']:
            return 'bullish'
        if df['close'] < df['open']:
            return 'bearish'

    def _determine_market_structure_random(self):
        rand = random.random()
        if rand > 0.5:
            return 'bullish'
        return 'bearish'

    ## Determines market structure
    def _determine_market_structure(self, df):
        return self._determine_market_structure_based_last_x_candles(df)

    ## Executes trading in a naive way.
    #  If bullish candle, buy at market price ("open" price)
    #  and sell after a fixed price above.
    #  If fixed price is higher than "close" sells whenever it gets to the order price.
    #  If bearish candle, sell at market price ("open" price)
    #  and buy after a fixed price below.
    #  If fixed price is lower than "close" buy whenever it gets to the order price
    def _double_trade_on_predicted_market_structure(self, df):
        market_value = df['open']
        order_volume_USD = 1
        market_structure = self._determine_market_structure(df)
        if market_structure == 'bullish':
            price = market_value
            order_result = self.place_order(
                side='buy', price=price, volume=order_volume_USD / market_value)
            if order_result is not None:
                price = market_value + 500
                order_result = self.place_order(
                    side='sell', price=price, volume=order_volume_USD / market_value)
        elif market_structure == 'bearish':
            price = market_value
            order_result = self.place_order(
                side='sell', price=price, volume=order_volume_USD / market_value)
            if order_result is not None:
                price = market_value - 500
                order_result = self.place_order(
                    side='buy', price=price, volume=order_volume_USD / market_value)

    def _trade_on_predicted_market_structure(self, df):
        market_value = df['open']
        order_volume_USD = 1
        market_structure = self._determine_market_structure(df)
        if market_structure == 'bullish':
            price = market_value + 500
            self.place_order(
                side='sell', price=price, volume=order_volume_USD / market_value)
        elif market_structure == 'bearish':
            price = market_value - 500
            self.place_order(
                side='buy', price=price, volume=order_volume_USD / market_value)

    def _trade(self, df):
        self._trade_on_predicted_market_structure(df)

    ## Naive algorithm to buy and sell at fixed price and volume,
    # based on the candle direction
    def order_based_on_candle_direction_TEST(self):
        # Load test data
        if not exists(self.FTX_DATASET_PATH):
            print("Dataset does not exist")
            return

        output_USD = pd.DataFrame({
                                  "day": [],
                                  "value": [],
                                  "type": []})
        output_BTC = pd.DataFrame({
                                  "day": [],
                                  "value": [],
                                  "type": []})

        current_balances = self.get_balances()
        previous_balances = copy.deepcopy(current_balances)
        previous_timestamp = self.get_start_timestamp()
        # Main loop of the algorithm
        while True:
            # Each iteration the platform will evaluate tasks
            # (For example getting the current test data,
            # or getting current market, in production mode).
            (running, _, timestamp) = self.evaluate(self._trade)
            if not running:
                break

            # Statistical data for plotting in an hourly window.
            if (timestamp - previous_timestamp >= timedelta(minutes=60)):
                # Generic tasks, collecting (and at the end plotting) profiling data
                self.BTC_per_window_of_interest.append(0)
                self.balance_USD_per_window_of_interest.append(0)
                current_balances = self.get_balances()
                length = len(self.BTC_per_window_of_interest) - 1
                self.BTC_per_window_of_interest[length] = \
                    current_balances['BTC']['total'] - previous_balances['BTC']['total']
                length = len(self.balance_USD_per_window_of_interest) - 1
                self.balance_USD_per_window_of_interest[length] = \
                    current_balances['USD']['total'] - previous_balances['USD']['total']
                previous_timestamp = timestamp
                previous_balances = copy.deepcopy(current_balances)

                length = len(self.BTC_per_window_of_interest) - 1
                output_BTC.loc[len(output_BTC)] = [
                    timestamp,
                    self.BTC_per_window_of_interest[length],
                    "BTC_window"]

                output_BTC.loc[len(output_BTC)] = [
                    timestamp,
                    current_balances['BTC']['total'],
                    "BTC_cumulative"]

                output_BTC.loc[len(output_BTC)] = [
                    timestamp,
                    current_balances['BTC']['free'],
                    "BTC_free"]

                length = len(self.balance_USD_per_window_of_interest) - 1
                output_USD.loc[len(output_USD)] = [
                    timestamp,
                    self.balance_USD_per_window_of_interest[length],
                    "USD_window"]

                output_USD.loc[len(output_USD)] = [
                    timestamp,
                    current_balances['USD']['total'],
                    "USD_cumulative"]

                output_USD.loc[len(output_USD)] = [
                    timestamp,
                    current_balances['BTC']['usdValue'],
                    "BTC_USD_value"]

                total = \
                    current_balances['BTC']['usdValue'] + current_balances['USD']['total']
                output_USD.loc[len(output_USD)] = [
                    timestamp,
                    total,
                    "Total_wealth_USD"]

                output_USD.loc[len(output_USD)] = [
                    timestamp,
                    current_balances['USD']['free'],
                    "USD_free"]

            self.cleanup_iteration()

        self.plot_historical(self.get_start_timestamp(), timestamp)

        fig = px.bar(
            output_USD,
            x="day",
            y="value",
            title='Gain over time USD',
            barmode='group',
            color="type")
        fig.show()

        fig = px.bar(
            output_BTC,
            x="day",
            y="value",
            title='Gain over time BTC',
            barmode='group',
            color="type")
        fig.show()
