from .detes_helper import db_helper as db
from .web_helper import ts_helper as th
from datetime import datetime as dt, timedelta
from pandas import DataFrame, concat

class fetcher:
    def __init__(self, start_date, region):
        self.db = db()
        self.th = th()
        self.__START_DATE = start_date
        self.region = region

    @staticmethod
    def format_date(date):
        return date.strftime("%Y%m%d")

    def update_quotes(self):
        if self.ch.cache_is_expired(type="quotes"):
            self.quotes = self.th.get_all_quotes()
            self.ch.cache_data(self.quotes)
        else:
            self.quotes = self.ch.load_data()

    def update_cal(self, region="us"):
        date = self.db.fetch_cal_last_date(region=region)
        if not date:
            date = self.__START_DATE
        start_date, end_date = date, dt.now().date().strftime("%Y%m%d")
        start_date = (dt.strptime(start_date, "%Y%m%d") + timedelta(days=1)).strftime(
            "%Y%m%d"
        )
        if end_date >= start_date:
            part_cal = self.th.get_dates(start_date, end_date, region=region)
            self.db.renew_calendar(part_cal, region=region)
        print(f"calendar update for {region} region completed")

    def update_us_stock_lst(self):
        """Insert new stocks and/or update info for all unfilled stocks"""

        # fetch trade list of stocks today (tushare)
        df = DataFrame({})
        for next_df in self.th.get_stock_lst():
            if next_df is None:
                break
            df = concat((df, next_df))

        if len(df):
            df = df.rename(columns={"ts_code": "code"})[["code"]]
            self.db.renew_stock_list(df, region="us")
        else:
            print("[fetcher] no added stocks")

        # update info for unfilled stocks
        stocks = self.db.get_stock_info(
            params={"industry": None, "sector": None, "has_option": None}, only_pk=True
        )
        tiks = self.th.get_stock_tickers(stocks)

        # iterate the above stocks and update one by one
        while True:
            try:
                # make yahooquery call
                code, sector, industry, has_option = next(tiks)
                meta = {}
                meta["code"] = code
                meta["sector"] = sector
                meta["industry"] = industry
                meta["has_option"] = has_option
                df = DataFrame([meta])
                self.db.renew_stock_list(df)
                print(f"{code} info has been recorded")

            except StopIteration:
                print("stock list update completed")
                break

    def update_stock_hist(self):
        """
        update stocks' historical data, starting from their last recorded dates
        """
        last_tr_date = self.db.get_last_trading_date()
        stocks, dates = [], []
        for d, c in self.db.get_latest_bars():
            if not d:
                d = dt.strptime(self.__START_DATE, "%Y%m%d").date()
            else:
                d += timedelta(days=1)

            if d <= last_tr_date:
                stocks.append(c)
                dates.append(d)
        for i, df in enumerate(
            self.th.fetch_stocks_hist(stocks, start_date=dates, end_date=last_tr_date)
        ):
            if df is None or not len(df):
                print(f"[fetcher] {stocks[i]} hist data update skipped")
                continue
            df = df.reset_index().rename(
                columns={
                    "Open": "open",
                    "High": "high",
                    "Low": "low",
                    "Close": "close",
                    "Volume": "vol",
                    "Date": "bar_date",
                }
            )
            df["code"] = stocks[i]
            self.db.renew_stock_hist(df, region="us")
            print(f"[fetcher] {stocks[i]} hist data updated")

        # only delist stocks after they are up to date
        self.db.delist_stocks()
