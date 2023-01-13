use detes;

if not exists (select *
from sys.tables
where name='stocks')
begin
  CREATE TABLE stocks
  (
    [exchange] nvarchar(5) not null,
    [code] nvarchar(6) not null,
    primary key (exchange, code)
  )
end;

if not exists (select *
from sys.tables
where name='us_cal')
BEGIN
  create table us_cal
  (
    [trade_date] date not null,
    [is_open] bit not null,
    primary key (trade_date, is_open)
  )
END;


if not exists (select *
from sys.tables
where name='cn_cal')
BEGIN
  create table cn_cal
  (
    [trade_date] date not null,
    [is_open] bit not null,
    primary key (trade_date, is_open)
  )
END;


if not exists (select *
from sys.tables
where name='hk_cal')
BEGIN
  create table hk_cal
  (
    [trade_date] date not null,
    [is_open] bit not null,
    primary key (trade_date, is_open)
  )
END;


if not exists(select *
from sys.tables
where name='cn_stock_list')
BEGIN
  create table cn_stock_list
  (
    [code] nvarchar(7) not null,
    [name] char(15),
    [area] char(6),
    [industry] char(12),
    [list_date] date,
    [delist_date] date,
    primary key (code)
  )
END;


if not exists(select *
from sys.tables
where name='us_stock_list')
begin
  create table us_stock_list
  (
    [code] nvarchar(7) not null,
    [sector] nvarchar(25),
    [exchange] nvarchar(5),
    [has_option] bit default null,
    [is_delisted]
      bit not null default 0,
    primary key
    (code)
  )
end;


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
    -- rolling moving average of 14 days
    [ma] float,
    [rsi] float,
    primary key (code, bar_date),
    constraint fk_code foreign key
    (code) references us_stock_list
    (code)
  )
END;

-- use detes;
-- select
--   top 10
--   *
-- from us_daily_bars
-- where code = 'AAPL'
-- order by bar_date desc

-- use detes
-- exec sp_rename 'dbo.us_daily_bars.ma14', 'close_pos_ma14', 'COLUMN'

-- alter table us_daily_bars
-- add open_pos_ma14 float;

-- alter table us_daily_bars
-- drop column open_pos_ma14;

-- update us_daily_bars
-- set close_pos_ma14=null, close_neg_ma14=null
-- where code='A' and bar_date='20000103'
