-- use detes;
-- alter table us_daily_bars
-- add streak int null;

-- where code = 'AAPL'
-- order by bar_date desc

-- use detes
-- exec sp_rename 'dbo.us_daily_bars.ma14', 'close_pos_ma14', 'COLUMN'

-- alter table us_daily_bars
-- add open_pos_ma14 float;

-- alter table us_daily_bars
-- drop column rsi;

-- use detes;
-- select *
-- from us_daily_bars
-- where code='BAC' and bar_date BETWEEN '2018-08-20' and '2018-09-10';

update us_daily_bars
set streak = null, close_neg_ma14 = null, close_pos_ma14 = null

select top 100 * from us_daily_bars
order by bar_date

select top 100 * from us_cal
order by trade_date desc
