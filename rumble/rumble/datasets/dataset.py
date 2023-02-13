from torch.utils.data import Dataset as DS
from ..tech.domains import Domains
from ...detes.detes_helper import db_helper as DB

from sqlalchemy.orm import Session
from sqlalchemy.sql import text
from os import path

import numpy as np


class rumbleset(DS, DB):
    def __init__(self):
        super(rumbleset, self).__init__()
        self.engine = super(rumbleset, self).connect_to_db(db_name="detes")

        self.dm = Domains()
        self.dm_samples = self.dm.streaks(5, min_date="2001-01-02")

    def __getitem__(self, index):
        """
        coefficient matrix: 32*63
        (T-126 trading days rows of daily data)
            relative strength index
            pos log return 14-day ma
            neg log return 14-day ma
            volume log return
            close log return
            open log return
            high to open log return
            low to open log return
            industry weighted log return
            industry volume log return
            stock's # of std dev. to the mean capital traded in industry
            sector weighted log return
            sector volume log return
            stock's # of std dev. to the mean capital traded in sector
            index log return
            index volume log return
        (another 14 rows of above coefficients in T-126 to T-63 trading days)
            ...
        """
        code, bar_date = self.dm_samples[index]
        return self.__build_sample(code, bar_date)

    def __build_sample(self, code, bar_date, day_offset: int = 0):
        with Session(self.engine) as sess:
            half_mat = sess.execute(
                text(
                    """
                    select
                    log([close] / ([close] - [close_neg_ma14])) neg_ma_ret,
                    log([close] / ([close] - [close_pos_ma14])) pos_ma_ret, 
                    ((100 - 100 / (1 + [close_pos_ma14] / abs(close_neg_ma14))) / 100 - .5) rsi,
                    log([vol]/lag([vol]) over (order by code asc, bar_date asc)) as vol_ret,
                    log([close]/(lag([close]) over (order by code asc, bar_date asc))) as close_ret,
                    log([open]/lag([open]) over (order by code asc, bar_date asc)) as open_ret,
                    log([high]/[open]) as high_diff,
                    log([low]/[open]) as low_diff,
                    bar_date
                    from us_daily_bars
                    where code = :code and bar_date <= :bar_date
                    order by bar_date desc
                    offset :offset rows
                    fetch next 63 rows only
                    """
                ),
                {"code": code, "offset": day_offset, "bar_date": bar_date},
            ).fetchall()

        agg_mat = np.stack(
            self.dm.get_agg_rets(row[-1], code, "industry") for row in half_mat
        )

        return agg_mat

    def __len__(self):
        return len(self.dm_samples)
