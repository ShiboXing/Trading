import pandas as pd
import subprocess as sp
import os
import pickle
from datetime import datetime as dt
from . import _CACHE_PATH

_hist_data_pth = os.path.join(_CACHE_PATH, "stock_hist.pkl")
_stock_list_pth = os.path.join(_CACHE_PATH, "stock_lst.pkl")
_timestamp_pth = os.path.join(_CACHE_PATH, "ts_lst.pkl")
_quotes_pth = os.path.join(_CACHE_PATH, "quotes.pkl")


class cache_helper:
    def __init__(self, cache_pth: str = _CACHE_PATH):
        if not os.path.exists(cache_pth):
            sp.run(f"mkdir -p {cache_pth}", check=True, shell=True)

        self.ts = {}
        self.ts_type = {
            "hist": _hist_data_pth,
            "list": _stock_list_pth,
            "quotes": _quotes_pth,
        }
        if os.path.exists(_timestamp_pth):
            try:
                self.ts = pickle.load(open(_timestamp_pth, "rb"))
            except EOFError:
                print("loading empty timestamp")

    def cache_is_expired(self, type="hist"):
        pth = self.ts_type[type]
        if pth not in self.ts or self.ts[pth].date() < dt.now().date():
            return True

        return False

    def cache_timestamp(self, pth):
        """
        change the pth's timestamp only, I/O bound
        """

        with open(_timestamp_pth, "wb+") as f:
            _ts = {}
            try:    
                _ts = pickle.load(f)
            except EOFError:
                pass
            _ts[pth] = dt.now()
            pickle.dump(_ts, f)
            print(f"{pth} timestamp cached")

    def cache_data(self, df, type="quotes"):
        write_pth = self.ts_type[type]
        self.cache_timestamp(write_pth)
        pickle.dump(df, open(write_pth, "wb"))
        print(f"{type} cached: ", df.values.shape)

    def load_data(self, type="quotes") -> pd.DataFrame:
        read_pth = self.ts_type[type]
        df = pd.read_pickle(read_pth)
        print(f"{type} loaded: ", df.values.shape)
        return df
