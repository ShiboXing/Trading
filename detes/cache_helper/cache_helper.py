import pandas as pd
import subprocess as sp
import datetime as dt
import os
import pickle
from . import _CACHE_PATH

_train_data_pth = os.path.join(_CACHE_PATH, "stock_hist.pkl")
_stock_list_pth = os.path.join(_CACHE_PATH, "stock_lst.pkl")
_timestamp_pth = os.path.join(_CACHE_PATH, "ts_lst.pkl")

class cache_helper:
    def __init__(self, cache_pth: str = _CACHE_PATH):
        if not os.path.exists(cache_pth):
            sp.run(f"mkdir -p {cache_pth}", check=True, shell=True)
        self.ts = {}
        if os.path.exists(_timestamp_pth):
            self.ts = pickle.load(open(_timestamp_pth, "rb"))

    def __cache_is_expired(self, pth):
        if self.ts[pth].date() < dt.now().date():
            return True

        return False

    def cache_timestamp(self, pth):
        self.ts[pth] = dt.now()

    def cache_train_data(self, df: pd.DataFrame):
        self.cache_timestamp(_train_data_pth)
        return df.to_pickle(_train_data_pth)
        

    def cache_stock_list(self, df: pd.DataFrame):
        self.cache_timestamp(_stock_list_pth)
        df.to_pickle(_stock_list_pth)

    def load_train_data(self):
        return pd.read_pickle(_train_data_pth)

    def get_list_pth(self):
        return pd.read_pickle(_stock_list_pth)
