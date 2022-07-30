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
        ex_col_name = "交易所英文名称Exchange(Eng)"
        hs = pd.read_excel(_hs300_url)
        zz = pd.read_excel(_zz500_url)
        stock_list = pd.concat(
            (hs[[code_col_name, ex_col_name]], zz[[code_col_name, ex_col_name]]), axis=0)
        stock_list = stock_list.astype({code_col_name: 'str'})

        for i in range(len(stock_list)):
            code_len = len(stock_list.iloc[i, 0])
            # add back the missing leading 0s
            if code_len < 6:
                stock_list.iloc[i, 0] = '0' * \
                    (6-code_len) + stock_list.iloc[i, 0]
            
            # add exchange code into stock code
            stock_ex = stock_list.iloc[i, 1].lower()
            if 'shenzhen' in stock_ex:
                stock_list.iloc[i, 0] += '.SZ'
            if 'shanghai' in stock_ex:
                stock_list.iloc[i, 0] += '.SH'

        stock_list = stock_list[[code_col_name]]
        return stock_list

    def get_stock_price_daily(codes: list, N):
        '''
        get the daily bars of a stock starting from today to N days back
        '''

        df = pd.DataFrame()
        window = 50
        for i in range(0, len(codes), window):
            end = max(i+window+1, len(codes))
            part_codes = ",".join(codes[i:end])
            end_date = date.today()
            start_date = end_date - timedelta(days=N)

            end_date_str = end_date.strftime("%Y%m%d")
            start_date_str = start_date.strftime("%Y%m%d")

            tmp = _pro_ts.daily(
                ts_code=part_codes, start_date=start_date_str, end_dat=end_date_str)

            df = pd.concat((df, tmp), axis=0)

        return df
