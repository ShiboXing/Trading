from torch.utils.data import Dataset as DS
from ..tech.domains import Domains


class rumbleset(DS):
    def __init__(self):
        """
        coefficient matrix (YTD rows of daily data)
            volume log return
            relative strength index
            pos log return 14-day ma
            neg log return 14-day ma
            close log return
            open log return
            high to open log return
            low to open log return
            industry weighted log return
            industry volume log return
            sector weighted log return
            sector volume log return
            stock index log return
            index volume log return
        """
        self.dm = Domains()

        pass
