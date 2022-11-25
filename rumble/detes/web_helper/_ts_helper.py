# -*- coding: UTF-8 -*-

import tushare as _ts
import pandas as pd
import time
from yfinance import Tickers
from re import search
from urllib.error import URLError
from datetime import date, timedelta, datetime as dt
from . import _TOKEN, _hs300_url, _zz500_url
from urllib3.exceptions import ReadTimeoutError
from requests.exceptions import ConnectionError


def retry_wrapper(func):
    def pause_and_retry(*args, **kwargs):
        while True:
            try:
                res = func(*args, **kwargs)
                break
            except Exception as e:
                if e.args:
                    if search("您每分钟最多访问该接口\d次", e.args[0]):
                        print(e.args[0])
                        print("[TUSHARE] 1-min web request limitation hit")
                        time.sleep(60)
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
    def get_stock_lst(self, region="us"):
        """
        request limitations:
            1. 5 times max per 24 hrs
            2. 2 times max per 1 min
        """
        today = dt.now().date().strftime("%Y%m%d")
        res = None
        for i in range(0, 24001, 6000):
            res = pd.concat((res, _pro_ts.us_daily(trade_date=today, offset=i)))
            time.sleep(31)  # failed requests might be counted against quota
        return res

    def get_stock_tickers(self, stocks=()):
        return Tickers(" ".join(stocks)).tickers

    def get_stock_hist(self, ts_codes: list, N):
        print("downloading stock hist...")
        df = pd.DataFrame()
        end_date = date.today()
        start_date = end_date - timedelta(days=N)
        window = 5000 // N  # tushare allows 5000 lines of data for every requests

        for i in range(0, len(ts_codes), window):
            end = min(i + window, len(ts_codes))
            part_codes = ",".join(ts_codes[i:end])

            end_date_str = end_date.strftime("%Y%m%d")
            start_date_str = start_date.strftime("%Y%m%d")

            while True:  # TODO: revise timeout handling
                try:
                    tmp = _pro_ts.daily(
                        ts_code=part_codes,
                        start_date=start_date_str,
                        end_dat=end_date_str,
                    )
                    df = pd.concat((df, tmp), axis=0)
                    break
                except (ReadTimeoutError, ConnectionError, OSError) as e:
                    print("daily bar request error, retrying...", e)

            print(f"{round(end/len(ts_codes) * 100, 2)}% fetched")

        return df

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
