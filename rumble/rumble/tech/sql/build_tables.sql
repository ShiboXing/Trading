
if not exists (select *
from sys.tables
where name='us_industry_signals')
BEGIN
    create table us_industry_signals
    (
        [industry] nvarchar(52) not null,
        [bar_date] date not null,
        [vol_ret] float, -- volume weighted average return
        [close_ret] float, -- close price weighted average return
        [vol_stddev] float, -- volume standard deviation
        [close_stddev] float, -- close price return standard deviation
        primary key (industry, bar_date)
    )
end;

if not exists (select *
from sys.tables
where name='us_sector_signals')
BEGIN
    create table us_sector_signals
    (
        [sector] nvarchar(25) not null,
        [bar_date] date not null,
        [vol_ret] float, -- volume weighted average return
        [close_ret] float, -- close price weighted average return
        [vol_stddev] float, -- volume standard deviation
        [close_stddev] float, -- close price return standard deviation
        primary key (sector, bar_date)
    )
end;