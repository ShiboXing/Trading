-- upsert the three major US stocks indexes
merge us_stock_list usl
using (values
    ('^DJI', 0),
    ('^GSPC', 0),
    ('^IXIC', 0)
) src (code, is_delisted)
on src.code in (
    select code from us_stock_list
) 
when not matched then
    insert (code, is_delisted)
    values (src.code, src.is_delisted)
;
