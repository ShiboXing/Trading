from typing import Callable
import pandas as pd

class rumbleset:
    def __init__(self, ch: cache_helper, batch_size: int):
        self.b_size = batch_size

    def build(self, domain: Callable):
        """
        TODO: load the data from disk by batches and process them with domain func
        """
        self.mat = pd.read_pickle(_stock_list_pth)
        self.mat = domain(self.mat)
