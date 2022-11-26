# -*- coding: UTF-8 -*-
import tushare as _ts
import pandas as pd
import time, heapq as pq
from yfinance import Tickers, download
from re import search
from urllib.error import URLError
from datetime import date, timedelta, datetime as dt
from . import _TOKEN, _hs300_url, _zz500_url
from urllib3.exceptions import ReadTimeoutError, ProtocolError
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
                        print("[web helper] daily requests limit reached")
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
    def get_stock_lst(self, region="us"):
        """
        request limitations:
            1. 5 times max per 24 hrs
            2. 2 times max per 1 min
        """

        res = None
        today = dt.now().date().strftime("%Y%m%d")
        for i in range(0, 24001, 6000):
            res = pd.concat((res, _pro_ts.us_daily(trade_date=today, offset=i)))
            time.sleep(31)  # failed requests might be counted against quota

        return res

    def get_stock_tickers(self, stocks=()):
        return Tickers(" ".join(stocks)).tickers

    def get_stocks_hist(self, codes, start_date: list or date, end_date: list or date):
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
            yield download(c, start=lo, end=hi + timedelta(days=1))

    # def get_stocks_hist(self, codes, start_date: list or str, end_date: list or str):
    #     """
    #     generator, to return the stock history data one by one
    #     codes, start_date and end_date lists share the same indices
    #     """
    #     start_islst, end_islst = type(start_date) == list, type(end_date) == list
    #     in_queue, wait_queue = [], []
    #     if start_islst:
    #         assert len(codes) == len(
    #             start_date
    #         ), "start dates length doesn't match codes"
    #         for i in range(len(codes)):
    #             pq.heappush(wait_queue, (start_date[i], i))
    #     else:
    #         wait_queue = [(start_date, i) for i in range(len(codes))]

    #     if end_islst:
    #         assert len(codes) == len(end_date), "end dates length doesn't match codes"
    #         if start_islst:
    #             assert len(start_date) == len(
    #                 end_date
    #             ), "end dates length doesn't match start dates"

    #     curr_date = min(start_date) if start_islst else start_date
    #     last_date = max(end_date) if end_islst else end_date
    #     req_str = ""
    #     while curr_date <= last_date:
    #         if wait_queue and wait_queue[0][0] == curr_date:
    #             while wait_queue and wait_queue[0][0] == curr_date:
    #                 _, next_i = pq.heappop(wait_queue)
    #                 if end_islst:
    #                     pq.heappush(in_queue, (end_date[next_i], next_i))
    #                 else:
    #                     in_queue = [(end_date, i) for i in range(len(codes))]

    #             req_str = " ".join(codes[i] for _, i in in_queue)

    #         yield download(req_str, start=curr_date, end=curr_date + timedelta(days=1))

    #         if in_queue and in_queue[0][0] == curr_date:
    #             while in_queue and in_queue[0] == curr_date:
    #                 pq.heappop(in_queue)

    #             req_str = " ".join(in_queue)

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
