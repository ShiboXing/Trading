import time, os
from rumble.detes import fetcher
from rumble.detes.cache_helper import cache_helper as ch

if __name__ == "__main__":

    os.environ['TZ'] = 'Asia/Shanghai'
    # os.environ['TZ'] = 'US/Eastern'
    time.tzset()
    
    ft = fetcher(400)
    ft.update_quotes()
    ft.fetch_all_hist()
    
    # _ch = ch()
    # hist = _ch.load_data("hist")
    # sig5 = day_streak(hist, 5, False)
    # _ch.cache_data(sig5, type="train")