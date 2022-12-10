from .detes_helper import db_helper as db
from .detes_helper import _us_stock_list_cols, _cn_stock_list_cols
from .web_helper import ts_helper as th

from torch.utils.data import Dataset


class StockSet(Dataset):
    def __init__(self):
        self.db = db()

    def __getitem__(self, idx):
        pass


class TechBuilder:
    def __init__(self):
        self.db = db()
        self.th = th()

    def update_rsi(self):
        self.db.iter_stocks_hist()
