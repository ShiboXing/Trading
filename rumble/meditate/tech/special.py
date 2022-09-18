from pandas import DataFrame as DF
from collections import deque
from operator import lt, gt
from time import time
from multiprocessing import Pool

import pandas as pd
import os


def __code_day_streak(data):
    """
    df: the hist data for a single stock code
    """
    df, days, is_up_streak = data
    # create column for each day's feature
    cols = {}
    features = ["open", "high", "low", "close"]
    for i in range(days):  # features * days
        for j in range(len(features)):
            cols = {**cols, f"{features[j]}{i}": []}
    comp = gt if is_up_streak else lt

    if len(df) <= days:
        return DF(cols)
    df = df.sort_values(["trade_date"])
    """
    use a finite state machine to determine streaks, 
    signal is valid is the final state is reached
    """
    state = 0
    signals = DF(columns=["ts_code", "trade_date"])
    window = deque([])  # cache for finite state machine
    cols = {}  # signal results
    for i in range(days):
        window.append(df.iloc[i][features])
        if len(window) > 1:
            state = (
                min(state + 1, days) if comp(window[-1].close, window[-2].close) else 0
            )

    for row in range(days, len(df)):
        """
        shift the sliding window, change state
        """
        window.popleft()
        window.append(df.iloc[row][features])
        state = min(state + 1, days) if comp(window[-1].close, window[-2].close) else 0

        assert days >= state >= 0

        """
        collect signals
        """
        if state == days:
            cols["ts_code"] = [df.iloc[row].ts_code]
            cols["trade_date"] = [df.iloc[row].trade_date]
            tmp_df = DF(cols)
            signals = pd.concat((signals, tmp_df))

    return signals


def day_streak(df: DF, days, is_up_streak=False):
    start_secs = time()

    df = df.sort_values(["ts_code", "trade_date"])
    df = df.reset_index().drop(
        columns=["index"]
    )  # reset index for better lookup runtime (unique and sorted)
    codes = set(df.ts_code)

    # calculate the streaks in multi-processes
    with Pool(os.cpu_count() - 1) as p:
        signal_lst = p.map(
            __code_day_streak,
            ((df[df.ts_code == c], days, is_up_streak) for c in codes),
            chunksize=10,
        )

    signals = pd.concat(signal_lst)
    signals = signals.sort_values(["ts_code", "trade_date"])
    signals = signals.reset_index().drop(
        columns=["index"]
    )  # reset index for better lookup runtime (unique and sorted)
    end_secs = time()
    print(f"{days} day_streak calculation took {(end_secs - start_secs) / 60} minutes")

    return signals


def day_streak_1up(df: DF, days):
    """
    convert day streaks of [days] long to [days+1]
    """
    df = df.sort_values(["ts_code", "trade_date"])
    new_streaks = DF(df.columns)
    for i in range(1, len(df)):
        if df.iloc[i]["ts_code"] == df.iloc[i - 1]["ts_code"]:
            pass
            # TODO: implement
