from rumble.detes import fetcher
from rumble.detes._loader import TechBuilder

import time, os
from yfinance import Tickers, download


if __name__ == "__main__":
    # os.environ["TZ"] = "Asia/Shanghai"
    os.environ["TZ"] = "US/Eastern"
    time.tzset()

    ft = fetcher("20000101", "us")
    ft.update_cal()
    ft.update_us_stock_lst()
    ft.update_stock_hist()

    # TODO: implement stock delisting
    ft.update_option_status()

    tb = TechBuilder()
    tb.update_ma()
    tb.update_streaks()

    # print("nums: ", hist.shape)
    # obj = rc.day_streak(
    #     hist[["ts_code", "trade_date", "open", "close", "vol"]].to_numpy().tolist(),
    #     5,
    #     True,
    # )
    # print("returned objsize : ", len(obj))

    # # fetch dataset samples
    # hist = hist.sort_values(by=["ts_code", "trade_date"])
    # for key in obj:
    #     print(key)
