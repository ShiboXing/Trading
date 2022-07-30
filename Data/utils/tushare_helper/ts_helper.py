from re import L
import tushare as _ts
import pandas as pd
from datetime import date, timedelta

from Data.utils.tushare_helper import *


class ts_helper:

    def __init__(self):
        global _ts
        global _pro_ts
        _ts.set_token(_TOKEN)
        _pro_ts = _ts.pro_api()

    def get_stock_list(self):

        code_col_name = "成分券代码Constituent Code"
        hs = pd.read_excel(_hs300_url)
        zz = pd.read_excel(_zz500_url)
        stock_list = pd.concat((hs[code_col_name], zz[code_col_name]), axis=0)
        stock_list = stock_list.astype({code_col_name: 'str'})

        for i in range(len(stock_list)):
            code_len = len(stock_list.iloc[i])
            if code_len < 6:
                stock_list.iloc[i] = '0' * (6-code_len) + stock_list.iloc[i]
        
        return stock_list

    def get_stock_price_daily(codes: list, N):
        '''
        get the daily bars of a stock starting from today to N days back
        '''

        end_date = date.today()
        start_date = end_date - timedelta(days=N)

        end_date_str = end_date.strftime("%Y%m%d")
        start_date_str = start_date.strftime("%Y%m%d")

        df = _pro_ts.daily(
            ts_code=codes, start_date=start_date_str, end_dat=end_date_str)
        return df
