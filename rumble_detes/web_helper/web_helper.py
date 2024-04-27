import yfinance as yf
import requests
from lxml import html

class web_helper:
    def __init__(self):
        pass

# Create a Session object
session = requests.Session()

# Make the request
res = session.get("https://www.slickcharts.com/sp500", headers={
    "User-agent": "*"
})

