import tushare as _ts

_TOKEN = "346f3cd2a2a3c16ba00575b2d502c3cdac87ba7b18de6fdd27e118b3"


class ts_helper:

    def __init__(self):
        global _ts
        global _pro_ts
        _ts.set_token(_TOKEN)
        _pro_ts = _ts.pro_api()

    def get_stock_list():
        
