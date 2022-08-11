from pandas import DataFrame as DF
from collections import deque

import pandas as pd


def make_day_streak(days: int, is_up_streak: False):

    # create column for each day's feature
    cols = {}
    features = ["open_chg", "hi_chg", "lo_chg", "close_chg"]
    for i in range(1, days + 1):
        for j in range(len(features)):
            cols = {**cols, f"{features[j]}{i}": []}

    def day_streak(df: DF):

        signals = DF(cols)
        feat_matrix = DF({f: [] for f in features})
        """
        TODO: revise signal filter logic
        """

        def compute_returns(window):
            global feat_matrix

            inds = window.index
            tmp_feats = {f: [] for f in features}
            cl0, op1, hi1, lo1, cl1 = (
                df.loc[inds[0]].close,
                df.loc[inds[1]].open,
                df.loc[inds[1]].high,
                df.loc[inds[1]].low,
                df.loc[inds[1]].close,
            )
            tmp_feats["open_chg"] = [(op1 - cl0) / cl0]
            tmp_feats["hi_chg"] = [(hi1 - op1) / op1]
            tmp_feats["lo_chg"] = [(lo1 - op1) / op1]
            tmp_feats["cl_chg"] = [(cl1 - op1) / op1]
            # feat_matrix = pd.concat([feat_matrix, tmp_feats])

            return 0

        df = df.sort_values(["ts_code", "trade_date"])
        df = df.reset_index().drop(
            columns=["index"]
        )  # reset index for better lookup runtime (unique and sorted)
        df.rolling(window=2).apply(compute_returns)

        """
        use a finite state machine to determine streaks, 
        signal is valid is the final state is reached
        """
        states = 0
        # for i in range(1, days+1):
        #     signals.append((

        #     ))

        # for i in range(len(df)):

        #     df.iloc[i]

    return day_streak
