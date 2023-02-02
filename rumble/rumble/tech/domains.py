from ...detes.detes_helper import db_helper
from sqlalchemy.orm import Session
from sqlalchemy.sql import text


class Domains(db_helper):
    def __init__(self):
        super().__init__()

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
