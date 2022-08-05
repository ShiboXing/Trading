from .tushare_helper import ts_helper as th
from .cache_helper import cache_helper as ch


class loader:

    def __init__(self, train_days):
        self.train_days = train_days
        self.th = th()
        self.ch = ch()
        self.stock_codes = self.th.get_stock_list()
        self.ch.cache_stock_list(self.stock_codes)

    def fetch_daily_prices(self):
        assert self.stock_codes is not None, "must fetch stock codes first"
        self.train_data = self.th.get_stock_price_daily(
            self.stock_codes.values.flatten(), self.train_days)

        self.ch.cache_hist_data(self.train_data)

    def update_quotes(self):
        assert self.stock_codes is not None, "must fetch stock codes first"
        self.quotes = self.th.get_real_time_quotes(
            self.stock_codes.values.flatten())
