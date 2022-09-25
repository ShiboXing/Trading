from re import L
from .cache_helper import cache_helper as ch
from .tushare_helper import ts_helper as th


class fetcher:
    quotes = None

    def __init__(self, train_days):
        self.train_days = train_days
        self.ch = ch()
        self.th = th()

    def fetch_all_hist(self):
        assert self.quotes is not None, "must fetch stock codes first"
        _dtype = "hist"
        if self.ch.cache_is_expired(_dtype):
            hist_data = self.th.get_stock_hist(self.quotes["ts_code"], self.train_days)
            self.ch.cache_data(hist_data, _dtype)
        else:
            print("hist data is not expired")

    def update_quotes(self):
        if self.ch.cache_is_expired(type="quotes"):
            self.quotes = self.th.get_all_quotes()
            self.ch.cache_data(self.quotes)
        else:
            self.quotes = self.ch.load_data()
