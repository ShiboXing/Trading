import time, os, argparse

from rumble.detes import fetcher
from rumble.detes._loader import TechBuilder
from rumble.rumble.tech.domains import Domains
from rumble.rumble.datasets.dataset import rumbleset
from sota.computer_vision.models.vgg import VGG
from datetime import datetime
from yfinance import Tickers, download


if __name__ == "__main__":
    """Just Die"""
    parser = argparse.ArgumentParser(description="specify the arguments of detes app")
    parser.add_argument('--cal', help='update the calendar', action="store_true")
    parser.add_argument("--hist", help="update history price", action="store_true")
    parser.add_argument("--list", help="update stock list", action="store_true")
    parser.add_argument("--ma", help="update moving average signals", action="store_true")
    parser.add_argument("--streak", help="update daily streak signals", action="store_true")
    args = parser.parse_args()
    # os.environ["TZ"] = "Asia/Shanghai"
    os.environ["TZ"] = "US/Eastern"
    time.tzset()
    
    ft = fetcher("20000101", "us")
    if args.cal:
        ft.update_cal()
    if args.list:
        ft.update_us_stock_lst() # weekly task
    if args.hist:
        ft.update_stock_hist()

    tb = TechBuilder()
    if args.ma:
        tb.update_ma()
    if args.streak:
        tb.update_streaks()

    # d = Domains()
    # d.update_agg_dates(is_industry=True)
    # d.update_agg_dates(is_industry=False)

    # d.update_agg_signals(is_industry=True)
    # d.update_agg_signals(is_industry=False)
    # index_rets = d.get_index_rets("2023-01-03", "2023-02-03")
