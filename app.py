from rumble.detes import fetcher
from rumble.detes.detes_helper import db_helper
from rumble.detes._loader import TechBuilder
import rumble_cpp as rc

import time, os
from operator import lt, gt


def rsi(closes):

    def ma(op):
        init_indx = -len(closes)
        avg = closes[init_indx] if op(closes[init_indx], 0) else 0
        for i in range(init_indx + 1, 0):
            inc = 0
            if op(closes[i], 0):
                inc = closes[i]
            avg = (avg * 13 + inc) / 14
        return avg

    lavg = abs(ma(lt))
    gavg = ma(gt)
    rs = gavg / lavg
    return 100 - 100 / (1 + rs)


if __name__ == "__main__":

    # os.environ["TZ"] = "Asia/Shanghai"
    os.environ["TZ"] = "US/Eastern"
    time.tzset()

    ft = fetcher("20000101", "us")
    ft.update_cal()
    # ft.update_us_stock_lst()
    # ft.update_stock_hist()
    # ft.update_option_status()

    tb = TechBuilder()
    tb.update_ma()

    import yfinance as yf
    tickers = yf.Tickers(["MSFT"])
    msft = yf.Ticker("MSFT")
    df = msft.history(period="1mo")
    rsi(df.Close.diff())
    
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
