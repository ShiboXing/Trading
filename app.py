import sys

# sys.path.insert(
#     0,
#     "/Users/shibox/repos/Trading-Container/Trading/build/lib.macosx-12-x86_64-cpython-310/",
# )
# i, j = 0, len(sys.path) - 1
# while i < j:
#     if "Trading" in sys.path[i]:
#         sys.path[i], sys.path[j] = sys.path[j], sys.path[i]
#         i, j = i + 1, j - 1
#     else:
#         i += 1

import time, os
import numpy as np
from rumble.detes import fetcher
from rumble.detes.cache_helper import cache_helper as ch
import rumble_cpp as rc

if __name__ == "__main__":

    os.environ["TZ"] = "Asia/Shanghai"
    # os.environ["TZ"] = "US/Eastern"
    time.tzset()

    ft = fetcher(400)
    ft.update_quotes()
    ft.fetch_all_hist()

    _ch = ch()
    hist = _ch.load_data("hist")[["ts_code", "trade_date", "open", "close"]]
    print("nums: ", hist.shape)
    # print(_strs.shape)
    obj = rc.day_streak(hist.to_numpy().tolist(), 5, True)
    print("returned obj: ", obj)
    # tc.day_streak((False, 0.123, 1, "f"))
