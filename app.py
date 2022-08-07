from detes import fetcher

ft = fetcher(365)
ft.update_quotes()
ft.fetch_all_hist()
