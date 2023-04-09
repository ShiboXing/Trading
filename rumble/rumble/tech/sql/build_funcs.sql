create or alter function get_sector_rets
(
    @sector VARCHAR(25),
    @query_date date
)
returns TABLE as return (
    select (vol * [open]) capital, close_ret, vol_ret
    from us_stock_list usl inner join (
        select code, [open], bar_date, vol,
        [close] / lag([close]) over (order by code asc, bar_date asc) close_ret, 
        [vol] / lag([vol]) over (order by code asc, bar_date asc) vol_ret
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
    select (vol * [open]) capital, close_ret, vol_ret
    from us_stock_list usl inner join (
        select code, [open], bar_date, vol,
        [close] / lag([close]) over (order by code asc, bar_date asc) close_ret,
        [vol] / lag([vol]) over (order by code asc, bar_date asc) vol_ret
        from us_daily_bars
    ) udb on udb.code = usl.code
    where bar_date = @query_date and industry = @industry
);
go

create or alter function get_agg_index_rets
(
    @start_date date,
    @end_date DATE
)
returns table
    return (
        select log(avg(ret)) avgret, log(avg(volret)) avgvol, bar_date from (
            select [close] / lag([close]) over (order by code asc, bar_date asc) ret, code, 
            [vol] / lag([vol]) over (order by code asc, bar_date asc) volret, bar_date
            from us_daily_bars
            where code in ('^IXIC', '^DJI', '^GSPC') 
        ) res
        where bar_date between @start_date and @end_date
        group by bar_date
    );
go
