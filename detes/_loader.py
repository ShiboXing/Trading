from .tushare_helper import ts_helper as th
from .cache_helper import cache_helper as ch


class loader:
    def __init__(self, train_days):
        self.train_days = train_days
        self.th = th()
        self.ch = ch()

        _dtype = "quotes"
        if self.ch.cache_is_expired(_dtype):
            self.quotes = self.th.get_all_quotes()
            self.ch.cache_data(self.quotes, _dtype)
        else:
            self.quotes = self.ch.load_data(_dtype)

    def fetch_all_hist(self):
        assert self.quotes is not None, "must fetch stock codes first"
        _dtype = "hist"
        if self.ch.cache_is_expired(_dtype):
            self.hist_data = self.th.get_stock_hist(
                self.quotes["ts_code"], self.train_days
            )
            self.ch.cache_data(self.hist_data, _dtype)
        else:
            self.hist_data = self.ch.load_data(_dtype)

    def update_quotes(self):
        assert self.quotes is not None, "must fetch stock quotes first"
        self.quotes = self.th.get_real_time_quotes(self.quotes.values.flatten())
