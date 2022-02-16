## Single sample stored in the alpha-beta filter containers.
class Sample:
    def __init__(self, price, t):
        self.price = price
        self.time = t

    def __repr__(self):
        return f"Sample({self.price}, {self.time})"


## Execute alpha-beta data filtering and prediction.
class AlphaBetaFilter:
    def __init__(self, init_sample, alpha=1, beta=0.1, price_change=0.0):
        ## Alpha parameter (to compensate price error)
        self.alpha = alpha
        ## Beta parameter (to compensate price change error)
        self.beta = beta
        ## Stores the price changes.
        self.price_change_list = [price_change]
        ## Stores all the price samples
        self.sample_list = [init_sample]
        self.predicted_price = 0
        self.predicted_price_change = 0

    @property
    def last_sample(self):
        return self.sample_list[-1]

    @property
    def last_price_change(self):
        return self.price_change_list[-1]

    ## Stores the new sample and predicts the new price.
    def add_sample(self, s: Sample):
        delta_t = s.time - self.last_sample.time
        self.predicted_price = \
            self.predicted_price + (delta_t * self.last_price_change)
        self.predicted_price_change = self.last_price_change
        error = s.price - self.predicted_price
        self.predicted_price = self.predicted_price + self.alpha * error
        self.predicted_price_change = \
            self.predicted_price_change + (self.beta / delta_t) * error

        # for debugging and results
        self.price_change_list.append(self.predicted_price_change)
        self.sample_list.append(s)
