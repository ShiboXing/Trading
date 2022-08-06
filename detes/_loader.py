from .tushare_helper import ts_helper as th
from .cache_helper import cache_helper as ch


class loader:
    def __init__(self, train_days):
        self.train_days = train_days
        self.th = th()
        self.ch = ch()

        _dtype = "list"
        if self.ch.cache_is_expired(_dtype):
            self.stock_codes = self.th.get_stock_list()
            self.ch.cache_data(self.stock_codes, _dtype)
        else:
            self.stock_codes = self.ch.load_data(_dtype)

    def fetch_all_quotes(self):
        """
        directly overwrites today's realtime quotes data
        """
        self.quotes = self.th.fetch_all_quotes()
        self.ch.cache_data(self.quotes, "quotes")

    def fetch_daily_prices(self):
        assert self.stock_codes is not None, "must fetch stock codes first"
        _dtype = "hist"
        if self.ch.cache_is_expired(_dtype):
            self.train_data = self.th.get_stock_price_daily(
                self.stock_codes.values.flatten(), self.train_days
            )
            self.ch.cache_data(self.train_data, _dtype)
        else:
            self.train_data = self.ch.load_data(_dtype)

    def update_quotes(self):
        assert self.stock_codes is not None, "must fetch stock codes first"
        self.quotes = self.th.get_real_time_quotes(self.stock_codes.values.flatten())
