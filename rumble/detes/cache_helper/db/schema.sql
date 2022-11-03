USE master;

IF NOT EXISTS (
   SELECT name
FROM sys.databases
WHERE name = N'detes'
)
begin
  CREATE DATABASE [detes]
end;

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
END;

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
END;

-- select name
-- from sys.tables;
-- EXEC sp_MSforeachtable @command1 = 'DROP TABLE ?'