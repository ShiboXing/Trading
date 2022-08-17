from pandas import DataFrame as DF
from collections import deque
from operator import lt, gt

import pandas as pd


def make_day_streak(days: int, is_up_streak=False):

    # create column for each day's feature
    cols = {}
    features = ["open", "high", "low", "close"]
    for i in range(days):  # features * days
        for j in range(len(features)):
            cols = {**cols, f"{features[j]}{i}": []}
    comp = gt if is_up_streak else lt

    def day_streak(df: DF):
        df = df.sort_values(["ts_code", "trade_date"])
        df = df.reset_index().drop(
            columns=["index"]
        )  # reset index for better lookup runtime (unique and sorted)

        """
        use a finite state machine to determine streaks, 
        signal is valid is the final state is reached
        """
        row = 0
        state = 0
        signals = DF(cols)
        window = deque([])  # cache for finite state machine

        while row < len(df):
            """
            collect signals
            """
            if state == days - 1:
                tmp_df = DF(cols)
                for i in range(len(window)):
                    for f in features:
                        cols[f"{f}{i}"] = [window[i][f]]
                cols["ts_code"] = df.loc[row].ts_code
                cols["trade_date"] = df.loc[row].trade_date
                signals = pd.concat((signals, tmp_df))

            if not row or df.loc[row].ts_code != df.loc[row - 1].ts_code:
                """
                switch code, fill the initial window
                """
                window = deque([])
                for i in range(days):
                    window.append(df.loc[row + i][features])
                    if len(window) > 1:
                        state = (
                            min(state + 1, days - 1)
                            if comp(window[-1].close, window[-2].close)
                            else 0
                        )
                row += 5
            else:
                """
                shift the sliding window, load signal if valid
                """
                window.popleft()
                window.append(df.loc[row][features])
                state = (
                    min(state + 1, days - 1)
                    if comp(window[-1].close, window[-2].close)
                    else 0
                )
                row += 1

            assert days - 1 >= state >= 0
            
        signals = signals.sort_values(["ts_code", "trade_date"])
        signals = signals.reset_index().drop(
            columns=["index"]
        )  # reset index for better lookup runtime (unique and sorted)
        return signals

    return day_streak
