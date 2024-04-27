import requests
from lxml import etree

class web_helper:
    def __init__(self):
        self.spy_ids = []


    def _get_spy_():
        """Retrive the list of stocks in spy"""
        session = requests.Session()

        res = session.get("https://www.slickcharts.com/sp500", headers={
            "User-agent": "*"
        })
        page = etree.HTML(res.content)
        symbols_a = page.xpath("//td[3]/a[contains(@href, '/symbol/')]")
        symbols = [s.text for s in symbols_a]
        