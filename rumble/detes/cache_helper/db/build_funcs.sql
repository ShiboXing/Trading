create or alter proc get_all_last_dates
as
begin
    select max(bar_date), l.code
    from us_stock_list l inner join us_daily_bars b
        on l.code = b.code
    group by l.code
end;
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
end;
go

-- exec get_last_trading_date @region = 'cn';
-- go

-- select *
-- from cn_cal