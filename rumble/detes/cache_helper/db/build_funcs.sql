create or alter proc get_all_last_dates
as
begin
    select max(bar_date), l.code
    from us_stock_list l inner join us_daily_bars b
        on l.code = b.code
    group by l.code
end
