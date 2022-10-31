import os
import subprocess as sp

_CACHE_PATH = os.path.expanduser("~/.trading_data")
_TRAIN_PATH = os.path.join(_CACHE_PATH, "train")
_hist_data_pth = os.path.join(_CACHE_PATH, "stock_hist.pkl")
_stock_list_pth = os.path.join(_CACHE_PATH, "stock_lst.pkl")
_timestamp_pth = os.path.join(_CACHE_PATH, "timestamp_lst.pkl")
_quotes_pth = os.path.join(_CACHE_PATH, "quotes.pkl")
_train_pth = os.path.join(_TRAIN_PATH, "train.pkl")

__all__ = [
    "_CACHE_PATH",
    "_TRAIN_PATH",
    "_hist_data_pth",
    "_stock_list_pth",
    "_timestamp_pth",
    "_quotes_pth",
    "_train_pth",
    "cache_helper",
]

from ._ch_helper import cache_helper
from ._ch_helper import db_helper
