from torch.utils.data import Dataset as DS
from ..tech.domains import Domains

class rumbleset(DS):
    def __init__(self):
        """
        coefficient matrix (rows of daily data)
        1. close log return
        2. open log return
        3. high to openn log return
        4. close to log return
        5. negative moving average log return
        6. positive moving average log return
        7.  sector close log return
        8.  sector open log return
        9.  sector high to open log return
        10. sector close to log return
        11. volume log return
        """
        self.dm = Domains()
        
        pass
