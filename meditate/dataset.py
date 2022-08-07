from typing import Callable
import pandas as pd

from detes.cache_helper import *


class dataset:
    def __init__(self, ch: cache_helper, batch_size: int):
        self.b_size = batch_size

    def build(self, domain: Callable):
        self.mat = pd.read_pickle(_stock_list_pth)
        pass
