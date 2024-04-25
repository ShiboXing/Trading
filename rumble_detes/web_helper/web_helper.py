import yfinance as yf
import requests
from lxml import html

class web_helper:
    def __init__(self):
        pass

res = requests.get("https://www.slickcharts.com/sp500")
