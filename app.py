from detes import loader

ld = loader(60)
ld.fetch_daily_prices()  
ld.update_quotes()
