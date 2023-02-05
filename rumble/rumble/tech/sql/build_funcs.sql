create or alter function get_sector_rets
(
    @sector_str VARCHAR(25),
    @query_date date
)
returns TABLE as return (
    select udb.code, (vol * [open]) capacity, open_ret, close_ret
    from us_stock_list usl inner join (
        select code, [open], bar_date, vol,
        ([open] / lag([open]) over (order by code asc, bar_date asc)) open_ret,
        ([close] / lag([close]) over (order by code asc, bar_date asc)) close_ret
        from us_daily_bars
    ) udb on udb.code = usl.code
    where sector = @sector_str and bar_date = @query_date
);
go

-- select top 10 * from get_sector_rets('Technology', '2023-01-05')
-- select * from us_daily_bars
-- where (code = 'AAPL' or code = 'AACAF') and 
--     bar_date between '2023-01-09' and '2023-01-10'