from re import L
from .tushare_helper import ts_helper as th
from .cache_helper import cache_helper as ch
from pandas import DataFrame as DF


class fetcher:
    def __init__(self, train_days):
        self.train_days = train_days
        self.th = th()
        self.ch = ch()

    def fetch_all_hist(self):
        assert self.quotes is not None, "must fetch stock codes first"
        _dtype = "hist"
        if self.ch.cache_is_expired(_dtype):
            hist_data = self.th.get_stock_hist(self.quotes["ts_code"], self.train_days)
            self.ch.cache_data(hist_data, _dtype)

    def update_quotes(self):
        _dtype = "quotes"
        self.quotes = self.th.get_all_quotes()
        self.ch.cache_data(self.quotes, _dtype)
