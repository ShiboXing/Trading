if not exists (select *
from sys.tables
where name='us_daily_bars')
BEGIN
  CREATE table us_daily_bars
  (
    [code] nvarchar(7) not null,
    [bar_date] date not null,
    [open] float not null,
    [close] float not null,
    [high] float not null,
    [low] float not null,
    [vol] float not null,
    [close_pos_ma14] float,
    [close_neg_ma14] float,
    [streak] int,
    primary key (code, bar_date),
    constraint fk_code foreign key
    (code) references us_stock_list (code)
  )
END;
