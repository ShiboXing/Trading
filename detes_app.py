from rumble.detes import fetcher
from rumble.detes._loader import TechBuilder

import time, os
from yfinance import Tickers, download


if __name__ == "__main__":
    """Just Die"""
    # os.environ["TZ"] = "Asia/Shanghai"
    os.environ["TZ"] = "US/Eastern"
    time.tzset()

    ft = fetcher("20000101", "us")
    ft.update_cal()
    ft.update_us_stock_lst() # weekly task
    ft.update_stock_hist()

    tb = TechBuilder()
    tb.update_ma()
    tb.update_streaks()
