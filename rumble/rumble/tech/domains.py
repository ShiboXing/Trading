from ...detes.detes_helper import db_helper
from sqlalchemy.orm import Session
from sqlalchemy.sql import text

from os import path


class Domains(db_helper):
    def __init__(self):
        super().__init__()
        sql_dir = path.join(path.dirname(__file__), "sql")
        self.engine = self.__connect_to_db(
            path.join(sql_dir, ".sql_creds"), db_name="detes"
        )
        self.__run_sqlfile(self.engine, path.join(sql_dir, "build_funcs.sql"))

    def get_sector_rets(self, sector: str, bar_date: str):
        """Calculate the weighted log return of one sector"""

        # get all the stock returns of the sector on a date
        with Session(self.engine) as sess:
            res = sess.execute(
                text(
                    """
                        select * from get_sector_rets(:sector, :bar_date)
                    """
                ),
                {"sector": sector, "bar_date": bar_date},
            )

            rets = res.fetchall()

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
