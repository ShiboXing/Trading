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
        self.engine = super().connect_to_db( db_name="detes"
        )
        super().run_sqlfile(self.engine, path.join(sql_dir, "build_funcs.sql"))

    def get_agg_rets(self, bar_date: datetime or str, filter_val: str, filter_key="sector"):
        """Get aggregate returns, through weighted averages of sector or industry """

        if filter_key not in ("sector", "industry"):
            raise ValueError("filter key value invalid!")
        
        # get all the stock returns of the sector on a date
        with Session(self.engine) as sess:
            res = sess.execute(
                text(
                    f"""
                    select * from get_{filter_key}_rets(:filter_val, :bar_date)
                    """
                ),
                {"filter_val": filter_val, "bar_date": bar_date},
            )
            rets = res.fetchall()

        rets = np.array(rets, dtype=np.float_)
        rets[:, 1] = np.log(rets[:, 1]) # element log on the ret column
        total_cap = np.sum(rets[:, 0]) # calculate the total capital traded
        rets[:, 0] /= total_cap # get weight ratio
        agg_ret = np.sum(rets[:, 0] * rets[:, 1]) # get weighted return
        
        return agg_ret, total_cap

        


    def get_streak_odds(self):
        with Session(self.engine) as sess:
            streak5 = sess.execute(
                text(
                    """
                select count(*) from us_daily_bars
                where bar_date between '2022-01-01' and '2023-01-01' and
                    streak > 4
            """
                )
            ).fetchone()[0]

            streak6 = sess.execute(
                text(
                    """
                select count(*) from us_daily_bars
                where bar_date between '2022-01-01' and '2023-01-01' and
                    streak > 5
            """
                )
            ).fetchone()[0]

            return float(streak6) / streak5
