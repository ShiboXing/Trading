create or alter function get_sector_rets
(
    @sector VARCHAR(25),
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
    where bar_date = @query_date and sector = @sector

);
go

create or alter function get_industry_rets
(
    @industry VARCHAR(52),
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
    where bar_date = @query_date and industry = @industry
);
go
