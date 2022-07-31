from .tushare_helper import ts_helper as th
# from Data.utils.cache_helper import tushare_helper as ch


class loader:

    def __init__(self, train_days):
        self.train_days = train_days
        self.th = th()
        # self.ch = ch()
        self.stock_codes = self.th.get_stock_list()

    def fetch_daily_prices(self):
        self.train_data = self.th.get_stock_price_daily(
            self.stock_codes.values.flatten(), self.train_days)
    