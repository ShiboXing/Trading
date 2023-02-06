create or alter function get_sector_rets
(
    @sector VARCHAR(25),
    @query_date date
)
returns TABLE as return (
    select (vol * [open]) capacity, close_ret
    from us_stock_list usl inner join (
        select code, [open], bar_date, vol,
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
    select (vol * [open]) capacity, close_ret
    from us_stock_list usl inner join (
        select code, [open], bar_date, vol,
        ([close] / lag([close]) over (order by code asc, bar_date asc)) close_ret
        from us_daily_bars
    ) udb on udb.code = usl.code
    where bar_date = @query_date and industry = @industry
);
go

create or alter function get_index_rets
(
    @industry VARCHAR(52),
    @query_date date
)
returns TABLE as return (
    select (vol * [open]) capacity, close_ret
    from us_stock_list usl inner join (
        select code, [open], bar_date, vol,
        ([close] / lag([close]) over (order by code asc, bar_date asc)) close_ret
        from us_daily_bars
    ) udb on udb.code = usl.code
    where bar_date = @query_date and industry = @industry
);
go

-- create or alter function get_avg_index_rets
-- (
--     @start_date date,
--     @end_date date,
-- )
-- returns table as return (
--     select 
-- )

