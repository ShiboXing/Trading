from pandas import DataFrame as DF


def make_day_streak(days: int, is_up_streak: False):
    def day_streak(df: DF):
        # create column for each day's feature
        cols = {}
        for i in range(1, days + 1):
            new_cols = {
                f"open_chg{i}": [],  # open - close pct chg, (post market)
                f"hi_chg{i}": [],  # hi - open pct chg (intra-day)
                f"lo_chg{i}": [],  # lo - open pct chg (intra-day)
                f"close_chg{i}": [],  # close - open pct chg (intra-day)
            }
            cols = {**new_cols, **cols}

        signals = DF()
        stocks = set(df.ts_code)
        dates = set(df.trade_date)

        """
        TODO: implement streak filter, return legal samples
        """

    return day_streak
