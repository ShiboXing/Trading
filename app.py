import sys

i, j = 0, len(sys.path) - 1
while i < j:
    if "Trading" in sys.path[i]:
        sys.path[i], sys.path[j] = sys.path[j], sys.path[i]
        i, j = i + 1, j - 1
    else:
        i += 1

import time, os
from rumble.detes import fetcher
from rumble.detes.cache_helper import cache_helper as ch
from rumble import tech_cpp as tc


class obj:
    def __init__(self):
        self.zxc = False
        self.a = 0.123
        self.b = 1
        self.c = "f"


if __name__ == "__main__":

    os.environ["TZ"] = "Asia/Shanghai"
    # os.environ['TZ'] = 'US/Eastern'
    time.tzset()

    # ft = fetcher(400)
    # ft.update_quotes()
    # ft.fetch_all_hist()

    # _ch = ch()
    # hist = _ch.load_data("hist")

    # sig5 = day_streak(hist, 5, False)
    # _ch.cache_data(sig5, type="train")
    o = obj()
    tc.day_streak(o)
    tc.day_streak((False, 0.123, 1, "f"))
