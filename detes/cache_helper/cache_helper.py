import pandas as pd
import subprocess as sp
import os
import pickle
from datetime import datetime as dt
from . import _CACHE_PATH

_hist_data_pth = os.path.join(_CACHE_PATH, "stock_hist.pkl")
_stock_list_pth = os.path.join(_CACHE_PATH, "stock_lst.pkl")
_timestamp_pth = os.path.join(_CACHE_PATH, "ts_lst.pkl")


class cache_helper:
    def __init__(self, cache_pth: str = _CACHE_PATH):
        if not os.path.exists(cache_pth):
            sp.run(f"mkdir -p {cache_pth}", check=True, shell=True)

        self.ts = {}
        self.ts_type = {
            "hist": _hist_data_pth,
            "list": _stock_list_pth,
        }
        if os.path.exists(_timestamp_pth):
            self.ts = pickle.load(open(_timestamp_pth, "rb"))

    def cache_is_expired(self, type="hist"):
        pth = self.ts_type[type]
        if pth not in self.ts or self.ts[pth].date() < dt.now().date():
            return True

        return False

    def cache_timestamp(self, pth):
        self.ts[pth] = dt.now()

    def cache_hist_data(self, df: pd.DataFrame):
        self.cache_timestamp(_hist_data_pth)
        df.to_pickle(_hist_data_pth)
        print("hist data cached: ", df.values.shape)

    def cache_stock_list(self, df: pd.DataFrame):
        self.cache_timestamp(_stock_list_pth)
        df.to_pickle(_stock_list_pth)
        print("stock list cached: ", df.values.shape)

    def load_train_data(self) -> pd.DataFrame:
        df = pd.read_pickle(_hist_data_pth)
        print("hist data loaded: ", df.values.shape)
        return df

    def load_stock_list(self) -> pd.DataFrame:
        df = pd.read_pickle(_stock_list_pth)
        print("stock list loaded: ", df.values.shape)
        return df
