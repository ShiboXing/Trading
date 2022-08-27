from re import L
from .tushare_helper import ts_helper as th
from .cache_helper import cache_helper as ch
from pandas import DataFrame as DF
from datetime import datetime as dt, time


class fetcher:
    quotes = None
    calendar = None

    def __init__(self, train_days):
        self.train_days = train_days
        self.th = th()
        self.ch = ch()

        # initialize trade calendar
        self.calendar = self.th.get_calendar()
        self.calendar = self.calendar.set_index("cal_date").sort_index()

    def fetch_all_hist(self):
        assert self.quotes is not None, "must fetch stock codes first"
        _dtype = "hist"
        if self.ch.cache_is_expired(_dtype):
            hist_data = self.th.get_stock_hist(self.quotes["ts_code"], self.train_days)
            self.ch.cache_data(hist_data, _dtype)
        else:
            print("hist data is not expired")

    def update_quotes(self):
        if self.quotes is None or self.__trade_is_on():
            self.quotes = self.th.get_all_quotes()

    def __trade_is_on(self, ex="") -> bool:
        # NYSE, NASDAQ: 09:30 - 16:00
        # SZSE, SHE: 09:30 - 11:30, 13:00 - 15:00
        # SEHK: 09:30 - 12:00, 13:00 - 16:00
        trade_windows = [(time(9, 30, 0), time(11, 30, 0)), (time(13, 0), time(15, 0))]

        today = dt.now().date().strftime("%Y%m%d")
        if self.calendar.loc[today].is_open == 1:
            for start, end in trade_windows:
                if start < dt.now().time() < end:
                    return True
        return False
