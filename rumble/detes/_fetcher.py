from re import L
from .cache_helper import db_helper as db
from .cache_helper import _us_stock_list_cols, _cn_stock_list_cols
from .tushare_helper import ts_helper as th
from datetime import datetime as dt, timedelta
from pandas import read_csv, DataFrame


class fetcher:
    def __init__(self, start_date, region):
        self.db = db()
        self.th = th()
        self.__START_DATE = start_date
        self.region = region

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
            date = self.db.fetch_cal_last_date(region=r)
            if not date:
                date = self.__START_DATE
            start_date, end_date = date, dt.now().date().strftime("%Y%m%d")
            start_date = (
                dt.strptime(start_date, "%Y%m%d") + timedelta(days=1)
            ).strftime("%Y%m%d")
            if end_date >= start_date:
                part_cal = self.th.get_dates(start_date, end_date, region=r)
                self.db.renew_calendar(part_cal, region=r)

    def update_us_stock_lst(self):
        # df = self.th.get_stock_lst()
        df = read_csv("stock_list.csv", index_col=False)
        df = df.rename(columns={"ts_code": "code"})[["code"]]
        df = df[~(df.code.str.contains("\."))]  # drop codes with dot
        self.db.renew_stock_list(df, region="us")

        # fill in stock list information
        stocks = self.db.get_stock_info(
            params={"exchange": None, "is_delisted": False}, only_pk=True
        )
        tiks = self.th.get_stock_tickers(stocks)

        for k, v in tiks.items():
            """performs web request with getter"""
            info = v.info

            if "sector" not in info:
                info["sector"] = None
            info["is_delisted"] = False
            if "exchange" not in info:
                info["exchange"] = None
                info["is_delisted"] = True
            elif (
                "longName" in info
                and info["longName"]
                and "delisted" in info["longName"]
            ):
                info["is_delisted"] = True
            if "quoteType" in info:  # ETFs don't have sector
                info["sector"] = "ETF" if info["quoteType"] == "ETF" else info["sector"]
            df = DataFrame(
                {
                    **{c: [info[c]] for c in ("sector", "exchange", "is_delisted")},
                    **{"code": k},
                }
            )
            self.db.renew_stock_list(df)
            print(f"{k} info has been recorded")

    def update_option_status(self):
        """
        record in the dataset whether each stock has options listed or not, (doesn't apply to cn region)
        """
        stocks = self.db.get_stock_info(params={"has_option": None}, only_pk=True)
        tiks = self.th.get_stock_tickers(stocks)
        for k, v in tiks.items():
            """perform web request with options getter"""
            df = DataFrame({"code": [k], "has_option": [bool(v.options)]})
            self.db.renew_stock_list(df, region="us")
            print(f"{k} option has been recorded")

    def update_stock_hist(self):
        """
        update stocks' historical data, starting from their last recorded dates
        """
        last_dates_and_codes = self.db.get_latest_bars()
        last_trading_date = self.db.get_last_trading_date()
        for d, c in last_dates_and_codes:
            if d < last_trading_date:
                pass
        # for s in stocks:
        # pass
