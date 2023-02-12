from ...detes.detes_helper import db_helper
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from os import path
from datetime import datetime

import numpy as np


class Domains(db_helper):
    def __init__(self):
        super().__init__()
        sql_dir = path.join(path.dirname(__file__), "sql")
        self.engine = super().connect_to_db(db_name="detes")
        super().run_sqlfile(self.engine, path.join(sql_dir, "build_funcs.sql"))

    def streaks(self, num: int, min_date="2000-01-01"):
        with Session(self.engine) as sess:
            samples = sess.execute(
                text(
                    """
                select code, bar_date from us_daily_bars
                where streak = :streak and bar_date >= :min_date
                order by code asc, bar_date asc
                """
                ),
                {"streak": num, "min_date": min_date},
            ).fetchall()

        return samples

    def get_index_rets(self, start_date, end_date):
        """Returns the log of mean returns of NASDAQ, DOW JONES, S&P 500"""
        rets = None
        with Session(self.engine) as sess:
            rets = sess.execute(
                text(
                    """
                select avgret, avgvol from get_agg_index_rets(:start, :end)
                order by bar_date
            """
                ),
                {
                    "start": start_date,
                    "end": end_date,
                },
            ).fetchall()

        return np.array(rets).transpose((1, 0))

    def get_agg_rets(self, bar_date: datetime or str, code: str, scope="sector"):
        code = "AAA"
        bar_date = "2020-09-11"
        """Get aggregate statistics, through weighted averages of sector or industry"""
        if scope not in ("sector", "industry"):
            raise ValueError("filter key value invalid!")

        # get all the stock returns of the sector on a date
        with Session(self.engine) as sess:
            scope_val = sess.execute(
                text(
                    f"""
                select {scope} 
                from us_stock_list
                where code = :code
                """
                ),
                {"code": code},
            ).fetchone()[0]

            code_cap = sess.execute(
                text(
                    """
                select ([vol] * [open])
                from us_daily_bars
                where code = :code and bar_date = :bar_date
                """
                ),
                {"code": code, "bar_date": bar_date},
            ).fetchone()[0]

            if scope_val:
                res = sess.execute(
                    text(
                        # set session properties to avoid division by zero error
                        f"""
                        SET ARITHABORT OFF
                        SET ANSI_WARNINGS OFF
                        select * from get_{scope}_rets(:filter_val, :bar_date)
                        """
                    ),
                    {"filter_val": scope_val, "bar_date": bar_date},
                )
                rets = res.fetchall()
            else:  # get single return values if scope info unavailable
                rets = sess.execute(
                    text(
                        """
                    SET ARITHABORT OFF
                    SET ANSI_WARNINGS OFF        
                    select cap, close_ret, vol_ret from (
                        select bar_date, ([vol] * [open]) cap,
                        [close] / lag([close]) over (order by code asc, bar_date asc) close_ret, 
                        [vol] / lag([vol]) over (order by code asc, bar_date asc) vol_ret
                        from us_daily_bars
                    ) res
                    where bar_date = :bar_date
                    """
                    ),
                    {"code": code, "bar_date": bar_date},
                ).fetchall()

        rets = np.nan_to_num(
            np.array(rets, dtype=np.float_), nan=1.0, neginf=1.0, posinf=1.0
        )
        cap_std, cap_mean = np.std(rets[:, 0]), np.mean(
            rets[:, 0]
        )  # calculate statistics of traded capital
        rets[:, 2][rets[:, 2] == 0] = 1  # prevent inf log values
        rets[:, 1:] = np.log(rets[:, 1:])  # element-wise log on the ret columns
        rets[:, 0] /= np.sum(rets[:, 0])  # get weight ratio, vol
        agg_ret = np.sum(rets[:, 0] * rets[:, 1])  # get weighted return
        vol_ret = np.sum(rets[:, 0] * rets[:, 2])  # get weighted volume return

        return (
            agg_ret,
            vol_ret,
            np.log(1 + max(min((code_cap - cap_mean) / cap_std / 10, 0.4), -0.4)),
        )  # a weirdly regularized stddev. counts
