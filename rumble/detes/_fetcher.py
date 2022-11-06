from re import L
from .cache_helper import db_helper as db
from .tushare_helper import ts_helper as th
from datetime import datetime as dt


class fetcher:
    def __init__(self, start_date, region):
        self.db = db()
        self.th = th()
        self.__START_DATE = start_date
        self.region = region

    def update_cal(self):
        return self.th.get_calendar(self.region, self.start_date)

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

    def update_cal(self):
        for r in ["us", "cn"]:
            date = self.db.fetch_last_date(region=r)
            if not date:
                date = self.__START_DATE
            end_date, start_date = dt.now().date().strftime("%Y%m%d"), date
            if end_date > start_date:
                part_cal = self.th.get_dates(start_date, end_date, region=r)
                print(part_cal)
                part_cal = part_cal.drop(columns="pretrade_date")
                self.db.renew_calendar(part_cal, region=r)
