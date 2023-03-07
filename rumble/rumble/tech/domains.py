from ...detes.detes_helper import db_helper
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from os import path, listdir
from datetime import datetime

import numpy as np


class Domains(db_helper):
    def __init__(self):
        super().__init__()
        sql_dir = path.join(path.dirname(__file__), "sql")
        self.engine = super().connect_to_db(db_name="detes")
        for sql_file in listdir(sql_dir):        
            super().run_sqlfile(self.engine, path.join(sql_dir, sql_file))

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

    def update_agg_dates(self, is_industry=True):
        """Insert the missing trading dates to aggregate signal tables"""
        agg = "industry" if is_industry else "sector"
        with Session(self.engine) as sess:
            sess.execute(
                text(
                    f"""
                    insert into us_{agg}_signals ({agg}, bar_date)
                    select distinct {agg}, trade_date
                    from us_stock_list, us_cal
                    where {agg} is not null
                        and {agg} != ''
                        and is_open = 1
                    except
                    select distinct {agg}, bar_date
                    from us_{agg}_signals
                    """
                )
            )
            sess.commit()

    def iter_sector_hist(self, filter_vol=True):
        """Fetch daily hist data of sector"""
        if filter_vol:
            filter_str = "where vol_ret is null"
        with Session(self.engine) as sess:
            res = sess.execute(
                text(
                    f"""
                    select * from us_industry_signals
                    {filter_str}
                    """
                )
            )
        pass

    def fetch_agg_rets(self, bar_date: datetime or str, scope_val: str, is_sector=True):
        scope = "sector" if is_sector else "industry"
        with Session(self.engine) as sess:
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
            return res.fetchall()

    def update_agg_rets(self, bar_date: datetime or str, scope_val: str, is_sector=True):
        """Calculate and fill the daily aggregate signals"""
        rets = self.fetch_agg_rets(bar_date, scope_val, is_sector=is_sector)
        rets = np.nan_to_num(
            np.array(rets, dtype=np.float_), nan=1.0, neginf=1.0, posinf=1.0
        )
        # ret: [capital traded, close price return pct, volume return pct]
        # calculate statistics of traded capital
        cap_std, cap_mean = np.std(rets[:, 0]), np.mean(
            rets[:, 0]
        )

        rets[:, 0] /= np.sum(rets[:, 0])  # get weight ratio, vol
        rets[:, 2][rets[:, 2] == 0] = 1  # prevent inf log values in vol returns (sometimes vol is 0)
        rets[:, 1:] = np.log(rets[:, 1:])  # element-wise log on the ret columns
        agg_ret = np.sum(rets[:, 0] * rets[:, 1])  # get weighted return
        vol_ret = np.sum(rets[:, 0] * rets[:, 2])  # get weighted volume return
        
        pass
