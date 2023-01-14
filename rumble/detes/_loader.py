from .detes_helper import db_helper as db
from .detes_helper import _us_stock_list_cols, _cn_stock_list_cols
from .web_helper import ts_helper as th
from torch.utils.data import Dataset
from multiprocessing import Pool

import rumble_cpp as rc
from ipdb import set_trace


class StockSet(Dataset):
    def __init__(self):
        self.db = db()

    def __getitem__(self, idx):
        pass


class TechBuilder:
    def __init__(self):
        self.db = db()
        self.th = th()

    def update_ma(self):
        for rows in self.db.iter_stocks_hist(
            nullma_only=True, select_close=True, select_prevma=True, select_pk=True
        ):
            averages = rc.ma(list(map(tuple, rows)))
            for i in range(len(rows)):
                row = rows[i]
                ma_row = averages[i]
                rows[i] = (row[0], row[1], ma_row[0], ma_row[1])
            self.db.update_ma(rows)
        print(f"finished update ma for {len(rows)} rows")

    def update_rsi(self):
        for rows in self.db.iter_stocks_hist():
            for i in range(len(rows)):
                rows[i] = (rows[i][0], rows[i][1].strftime("%Y%m%d"), rows[i][3])
