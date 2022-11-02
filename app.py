import time, os
import numpy as np
from rumble.detes import fetcher
from rumble.detes.cache_helper import cache_helper as ch
from rumble.detes.cache_helper import db_helper
import rumble_cpp as rc

if __name__ == "__main__":

    # os.environ["TZ"] = "Asia/Shanghai"
    os.environ["TZ"] = "US/Eastern"
    time.tzset()
    db_helper()
    ft = fetcher("20080101", "us")
    ft.update_quotes()
    ft.fetch_all_hist()

    _ch = ch()
    hist = _ch.load_data("hist")
    hist = hist.astype({"vol": "int"})
    print("nums: ", hist.shape)
    obj = rc.day_streak(
        hist[["ts_code", "trade_date", "open", "close", "vol"]].to_numpy().tolist(),
        5,
        True,
    )
    print("returned objsize : ", len(obj))

    # fetch dataset samples
    hist = hist.sort_values(by=["ts_code", "trade_date"])
    for key in obj:
        print(key)
