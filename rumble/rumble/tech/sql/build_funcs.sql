create or alter view get_sector_rets
as 
    select udb.code, (vol * [open]) capacity, bar_date, open_ret, close_ret
    from us_stock_list usl inner join (
        select code, [open], bar_date, vol,
        ([open] - lag([open]) over (order by code asc, bar_date asc)) open_ret,
        ([close] - lag([close]) over (order by code asc, bar_date asc)) close_ret
        from us_daily_bars 
    ) udb on udb.code = usl.code
    where sector = (
        select sector 
        from us_stock_list
        where code = 'AAPL'
    ) and udb.bar_date = '2023-01-04'
go

select top 10 * from get_sector_rets
select * from us_daily_bars
where (code = 'AAPL' or code = 'AATC') and 
    bar_date between '2023-01-03' and '2023-01-04'