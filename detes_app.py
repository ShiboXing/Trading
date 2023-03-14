from rumble.detes import fetcher
from rumble.detes._loader import TechBuilder
from rumble.rumble.tech.domains import Domains
from rumble.rumble.datasets.dataset import rumbleset
from sota.computer_vision.models.vgg import VGG

from datetime import datetime
import time, os
from yfinance import Tickers, download


if __name__ == "__main__":
    """Just Die"""
    # os.environ["TZ"] = "Asia/Shanghai"
    os.environ["TZ"] = "US/Eastern"
    time.tzset()

    # ft = fetcher("20000101", "us")
    # ft.update_cal()
    # ft.update_us_stock_lst() # weekly task
    # ft.update_stock_hist()

    # tb = TechBuilder()
    # tb.update_ma()
    # tb.update_streaks()

    d = Domains()
    d.update_agg_dates(is_industry=True)
    d.update_agg_dates(is_industry=False)

    d.update_agg_signals(is_industry=True)
    d.update_agg_signals(is_industry=False)
    # index_rets = d.get_index_rets("2023-01-03", "2023-02-03")
