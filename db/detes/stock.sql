USE master
GO
IF NOT EXISTS (
   SELECT name
FROM sys.databases
WHERE name = N'detes'
)
begin
  CREATE DATABASE [detes]
end
GO

use detes
GO

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
end
GO

if not exists (select *
from sys.tables
where name='daily_bars')
BEGIN
  CREATE table daily_bars
  (
    [exchange] nvarchar(6) not null,
    [code] nvarchar(6) not null,
    [bar_date] date not null,
    [open] float not null,
    [close] float not null,
    [high] float not null,
    [low] float not null,
    [vol] float not null,
    primary key (exchange, code, bar_date)
  )
END
go

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
END
GO

if not exists (select *
from sys.tables
where name='ch_cal')
BEGIN
  create table ch_cal
  (
    [trade_date] date not null,
    [is_open] bit not null,
    primary key (trade_date, is_open)
  )
END
GO

if not exists (select *
from sys.tables
where name='exchanges')
BEGIN
  create table exchanges
  (
    [ex_code] nvarchar(6) not null,
    [country_code] NVARCHAR(3) not null,
    primary key (ex_code, country_code)
  )
END
GO

insert into stocks
values('SZ', '000003')
insert into daily_bars
values('NYSE', 'BIDU', '2019-12-10', 79.01, 77.23, 80.12, 75.12, 1378888.27);
GO

select *
from stocks;
select *
from daily_bars;
select *
from us_cal;
select *
from ch_cal;
GO