from torch.utils.data import Dataset as DS
from ..tech.domains import Domains


class rumbleset(DS):
    def __init__(self):
        """
        coefficient matrix (YTD rows of daily data)
            volume log return
            close log return
            open log return
            high to open log return
            low to open log return
            negative moving average log return
            positive moving average log return
            industry weighted log return
            sector weighted log return
            stock index log return
        """
        self.dm = Domains()

        pass
