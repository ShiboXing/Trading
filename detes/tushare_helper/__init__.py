_TOKEN = "346f3cd2a2a3c16ba00575b2d502c3cdac87ba7b18de6fdd27e118b3"
_hs300_url = "https://csi-web-dev.oss-cn-shanghai-finance-1-pub.aliyuncs.com/static/html/csindex/public/uploads/file/autofile/closeweight/000300closeweight.xls"
_zz500_url = "https://csi-web-dev.oss-cn-shanghai-finance-1-pub.aliyuncs.com/static/html/csindex/public/uploads/file/autofile/closeweight/000905closeweight.xls"
_lapse = 0.5  # seconds to sleep after a single request

__all__ = ["_TOKEN", "_lapse", "_hs300_url", "_zz500_url", "ts_helper"]

from ._ts_helper import ts_helper
