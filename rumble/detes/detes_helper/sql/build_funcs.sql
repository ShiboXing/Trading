create or alter view get_all_last_dates
as
    select max(bar_date) last_date, l.code
    from us_stock_list l left join us_daily_bars b
        on l.code = b.code
    where is_delisted = 0
    group by l.code
go

create or alter function get_last_trading_date (
    @region nvarchar(2) = 'us'
)
    returns date
    begin
        declare @max_date date
        if @region = 'cn'
        begin
            select @max_date = (
                select max(trade_date)
                from cn_cal
                where is_open=1
            )
        end
        else if @region = 'us'
        begin
            select @max_date = (
                select max(trade_date)
                from us_cal
                where is_open=1
            )
        end
        return @max_date
    end
go

create or alter function get_delisted_stocks()
returns @old_stocks table (last_date date, code VARCHAR(7), diff int)
    begin
        declare @last_date date;
        set @last_date = dbo.get_last_trading_date('us')

        insert into @old_stocks
        select * from (
            select *,
                datediff(day, last_date, @last_date) diff_days
            from get_all_last_dates
        ) tmp
        where tmp.diff_days > 14

        return;
    end
go
