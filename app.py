from detes import fetcher
from meditate.tech.special import day_streak
from detes.cache_helper import cache_helper as ch

if __name__ == "__main__":
    ft = fetcher(400)
    ft.update_quotes()
    ft.fetch_all_hist()
    
    _ch = ch()
    hist = _ch.load_data("hist")
    sig5 = day_streak(hist, 5, False)