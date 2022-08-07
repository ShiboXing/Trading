from typing import Callable
import detes


class dataset:
    def __init__(self, ft: detes.fetcher):
        self.ft = ft

    def build(self, domain: Callable):
        self.ft.fetch_all_hist()  # prepare all hist data
        """
        TODO: implement building dataset
        """
        pass
