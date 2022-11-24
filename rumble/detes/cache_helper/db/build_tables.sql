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
    primary key (code, bar_date),
    constraint fk_code foreign key
    (code) references us_stock_list
    (code)
  )
END;


-- insert into us_daily_bars
--   (code, bar_date, [open], [close], high, low, vol)
-- values('AAPL', '20221111', 1, 1, 1, 1, 1),
--   ('U', '20211101', 1, 1, 1, 1, 1)

-- select *
-- from us_stock_list
-- where exchange is null and is_delisted = 0;
-- where code like '%.%';

-- use detes;
-- exec sp_rename 'us_stock_list.industry', 'sector', 'COLUMN';

-- alter table us_stock_list
-- add has_option bit null;
-- drop column city;

-- use detes;
-- select *
-- from us_cal

-- select *
-- from cn_cal;

-- alter table us_stock_list
-- alter column sector varchar(25);

-- select top 6000
--   *
-- from us_stock_list
-- where exchange is null;
-- where code = 'LDEM';

-- delete from us_stock_list
-- where code = 'LDEM'

-- alter table us_stock_list
-- add is_delisted bit not null default 0;

-- update us_stock_list 
-- set name='acac', city='death'
-- where code = 'AAAAA';

-- delete from us_cal
-- where trade_date > '2020-03-30';
-- delete from cn_cal
-- where trade_date > '2018-02-12';

-- select name
-- from sys.tables;
-- use detes;
-- EXEC sp_MSforeachtable @command1 = '
-- DROP TABLE ?'
