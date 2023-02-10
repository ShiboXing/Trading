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

    def get_agg_rets(
        self, bar_date: datetime or str, filter_val: str, filter_key="sector"
    ):
        """Get aggregate returns, through weighted averages of sector or industry"""

        if filter_key not in ("sector", "industry"):
            raise ValueError("filter key value invalid!")

        # get all the stock returns of the sector on a date
        with Session(self.engine) as sess:
            res = sess.execute(
                text(
                    # set session properties to avoid division by zero error
                    f"""
                    SET ARITHABORT OFF
                    SET ANSI_WARNINGS OFF
                    select * from get_{filter_key}_rets(:filter_val, :bar_date)
                    """
                ),
                {"filter_val": filter_val, "bar_date": bar_date},
            )
            rets = res.fetchall()

        rets = np.nan_to_num(np.array(rets, dtype=np.float_), nan=1.0, neginf=1.0, posinf=1.0)
        rets[:, 2][rets[:, 2] == 0] = 1 # prevent inf log values 
        rets[:, 1:] = np.log(rets[:, 1:])  # element-wise log on the ret columns
        rets[:, 0] /= np.sum(rets[:, 0])  # get weight ratio, vol 
        agg_ret = np.sum(rets[:, 0] * rets[:, 1])  # get weighted return
        vol_ret = np.sum(rets[:, 0] * rets[:, 2])  # get weighted volume return

        return agg_ret, vol_ret
