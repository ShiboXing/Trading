
if not exists (select *
from sys.tables
where name='us_stock_signals')
BEGIN
    create table us_stock_signals
    (
        [code] nvarchar(7) not null,
        [bar_date] date not null,
        [ind_vol_ret] float, -- industry scores
        [ind_close_ret] float,
        [ind_stddev_cnt] float,
        [sec_vol_ret] float, -- sector scores
        [sec_close_ret] float,
        [sec_stddev_cnt] float,
        primary key (code, bar_date),
        constraint fk_signal_code foreign key
        (code) references us_stock_list (code)
    )
end;