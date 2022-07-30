import tushare as ts

_TOKEN = "346f3cd2a2a3c16ba00575b2d502c3cdac87ba7b18de6fdd27e118b3"
ts.set_token(_TOKEN)

def get_pro():
    return ts.pro_api()

def get_ts():
    return ts
