create or alter proc get_all_last_dates
as
    begin
        select max(bar_date), l.code
        from us_stock_list l left join us_daily_bars b
            on l.code = b.code
        where is_delisted = 0
        group by l.code
    end
    return
go

create or alter proc get_last_trading_date
    @region nvarchar(2)
as 
    begin
        if @region = 'cn'
        begin
            select max(trade_date)
            from cn_cal
            where is_open=1
        end
        else if @region = 'us'
        begin
            select max(trade_date)
            from us_cal
            where is_open=1
        end
    end
    return
go

-- create or alter function delist_stocks()
-- returns @stocks_info table (bar_date date, code varchar(7), diff int)
--     begin
--         declare @last_date table (tmp_date date);
--         insert into @last_date 
--         select * from (exec get_last_trading_date 'us');
--         insert into @stocks_info
--         select max(bar_date), h.code, 
--         datediff(day, max(bar_date), (
--             select * from @last_date)
--         )
--         from us_stock_list h inner join us_daily_bars l
--         on h.code = l.code
--         where is_delisted = 0
--         group by h.code;
--         return
--     end
-- go


-- select * from dbo.delist_stocks();
-- declare @tmp_stocks table (d date, c VARCHAR(7), i int);
-- select * from delist_stocks;
-- select code from us_stock_list uss inner join
--     @tmp_stocks ts on ts.c = uss.code
-- where i > 7;
    
