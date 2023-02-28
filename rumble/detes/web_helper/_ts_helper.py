# -*- coding: UTF-8 -*-
import tushare as _ts
import pandas as pd
import time
from yahooquery import Ticker
from yfinance import download
from re import search
from urllib.error import URLError
from datetime import date, timedelta, datetime as dt
from . import _TOKEN
from requests.exceptions import ConnectionError


def retry_wrapper(func):
    def pause_and_retry(*args, **kwargs):
        while True:
            try:
                res = func(*args, **kwargs)
                break
            except ConnectionError as e:
                if "Connection aborted." in e.args:
                    print("[web helper] connection error, retrying")
            except Exception as e:
                if e.args:
                    if search("您每分钟最多访问该接口\d次", e.args[0]):
                        print(e.args[0])
                        print("[TUSHARE] 1-min web request limitation hit")
                        time.sleep(60)
                    elif "抱歉，您每天最多访问该接口" in e.args[0]:
                        print("[web helper] tushare daily requests limit reached")
                        return None
                    else:
                        raise e
        return res

    return pause_and_retry


class ts_helper:
    def __init__(self):
        global _ts
        global _pro_ts
        _ts.set_token(_TOKEN)
        _pro_ts = _ts.pro_api()

    @staticmethod
    def format_date(date):
        return date.strftime("%Y-%m-%d")

    def get_all_quotes(self):
        print("downloading all stock quotes")
        while True:
            try:
                quotes = _ts.get_today_all()[
                    ["code", "name", "open", "turnoverratio", "per"]
                ]
                break
            except TimeoutError:
                print("quotes timeout: retrying...")
                pass
            except URLError:
                print("quotes urlerror: retrying...")
                pass

        stock_info = _pro_ts.query("stock_basic")[
            ["ts_code", "symbol", "industry", "market"]
        ]  # get all listed stocks' info
        quotes = quotes.set_index("code").join(
            stock_info.set_index("symbol"), how="inner"
        )

        return quotes

    @retry_wrapper
    def __ts_get_lst(self, trade_date, offset, region="us"):
        return _pro_ts.us_daily(trade_date=trade_date, offset=offset)

    def get_stock_lst(self, region="us"):
        """
        request limitations:
            1. 5 times max per 24 hrs
            2. 2 times max per 1 min
        """
        """
        TODO: cache last offset and start iterating at different offset each trading day
        """
        today = dt.now().date().strftime("%Y%m%d")
        for i in range(0, 24001, 6000):
            yield self.__ts_get_lst(today, i)
            time.sleep(31)  # failed requests might be counted against quota

    def get_stock_tickers(self, stocks=()):
        """Generator for ticker info, makes call during next()"""
        for code in stocks:
            tk = Ticker(code)
            yield code, tk.asset_profile[code]
            
    def fetch_stocks_hist(
        self, codes, start_date: list or date, end_date: list or date
    ):
        """
        generator, to return the stock history data one by one
        codes, start_date and end_date lists share the same indices
        start_date: inclusive
        end_date: inclusive
        """
        start_islst, end_islst = type(start_date) == list, type(end_date) == list
        if start_islst:
            assert len(codes) == len(
                start_date
            ), "start dates length doesn't match codes"

        if end_islst:
            assert len(codes) == len(end_date), "end dates length doesn't match codes"
            if start_islst:
                assert len(start_date) == len(
                    end_date
                ), "end dates length doesn't match start dates"

        for i, c in enumerate(codes):
            lo = start_date[i] if start_islst else start_date
            hi = end_date[i] if end_islst else end_date
            df = download(c, start=lo, end=hi + timedelta(days=1))

            # guard for yfinance fetch-out-of-range by 1 day error
            if len(df) and df.index[0].to_pydatetime().date() < lo:
                df = df.drop(df.index[0])
            yield df

    def get_real_time_quotes(self, codes: list):
        window = 30
        df = pd.DataFrame()

        for i in range(0, len(codes), window):
            end = max(i + window, window)
            part_codes = [
                code[:-3] for code in codes[i:end]
            ]  # rid code of exchange code

            tmp = _ts.get_realtime_quotes(part_codes)
            df = pd.concat((df, tmp), axis=0)

        return df

    @retry_wrapper
    def get_dates(self, start_date, end_date, region="us"):
        res = None
        if region == "us":
            res = _pro_ts.us_tradecal(start_date=start_date, end_date=end_date)
        elif region == "cn":
            res = _pro_ts.trade_cal(start_date=start_date, end_date=end_date)
        return res

    @staticmethod
    def today():
        """
        get today's date string
        """
        return date.today().strftime("%Y%m%d")

    def __Nday(self, N: int):
        """
        get minus N day's date string
        """
        return (date.today() - timedelta(days=N)).strftime("%Y%m%d")
