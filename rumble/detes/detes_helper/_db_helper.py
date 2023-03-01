import pandas as pd
import os

from sys import getsizeof
from datetime import datetime as dt
from sqlalchemy import create_engine, column
from sqlalchemy.sql import text
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session
from . import _stock_table_cols

class db_helper:
    @staticmethod
    def tuple_transform(rows):
        """
        Decorator used to parse rows from sqlalchemy to list of native python tuples
        """
        return list(map(tuple, rows))

    def connect_to_db(self, db_name):
        creds_pth = os.path.join(self.__sql_dir, ".sql_creds")
        with open(creds_pth, "r") as f:
            server, port, username, password, driver = f.readline().split(",")

        connect_url = URL.create(
            "mssql+pyodbc",
            username=username,
            password=password,
            host=server,
            port=port,
            database=db_name,
            query=dict(
                driver=driver,
                TrustServerCertificate="yes",
            ),
        )

        engine = create_engine(
            connect_url, echo=False, isolation_level="READ COMMITTED"
        )

        return engine

    def run_sqlfile(self, engine, schema_pth):
        conn = engine.raw_connection()
        with open(schema_pth, "r") as f:
            sql_str = f.read()
        for cmd in sql_str.split("\ngo\n"):
            if cmd:
                conn.execute(cmd)
                conn.commit()

    def __init__(self):
        self.__sql_dir = os.path.join(os.path.dirname(__file__), "sql")

        # build db if needed
        tmp_engine = self.connect_to_db(db_name="master")
        self.run_sqlfile(
            tmp_engine, os.path.join(self.__sql_dir, "schema", "build_schema.sql")
        )

        # build tables and funcs if needed
        self.engine = self.connect_to_db(db_name="detes")
        for f in sorted(os.listdir(os.path.join(self.__sql_dir, "data"))):
            self.run_sqlfile(self.engine, os.path.join(self.__sql_dir, "data", f))

    def __get_table_name(self, region="us", type="lst"):
        assert region in ("us", "cn", "hk"), "region parameter is incorrect"
        assert type in ("lst", "cal", "hist"), "table type parameter is incorrect"
        if type == "lst":
            return f"{region}_stock_list"
        elif type == "cal":
            return f"{region}_cal"
        elif type == "hist":
            return f"{region}_daily_bars"

    def __format_filter_str(self, keys, sep="and"):
        return f" {sep} ".join([f"{k}= :{k}" for k in keys])

    def iter_stocks_hist(
        self,
        price_lag=0,
        nullma_filter=False,
        nullstreak_filter=False,
        select_close=False,
        select_prevma=False,
        select_prevstreak=False,
        select_pk=False,
        lag_degree=1,
    ):
        """
        use generator to fetch stock daily bars
        get cross-row data in every row
        """
        batch_size = 1024 * 1024 * 100  # 100MB batch size
        row_cnt = 0

        # get row count in each batch based row mem size
        with Session(self.engine) as sess:
            first_row = sess.execute(
                text(
                    f"""
                select top 1 * from us_daily_bars
                """
                )
            ).fetchone()
            row_size = 0
            for n in first_row:
                row_size += getsizeof(n)
            row_cnt = int(batch_size // row_size)

        filter = ""
        res_alias = "bars_res"
        cols = []
        if nullma_filter:
            filter = f"where {res_alias}.[close_pos_ma14] is NULL"
        if nullstreak_filter:
            filter = f"where {res_alias}.[streak] is NULL"
        if select_pk:
            cols.append(f"{res_alias}.[code]")
            cols.append(f"{res_alias}.[bar_date]")
        if select_close:
            cols.append(f"{res_alias}.[close]")
            for i in range(1, lag_degree + 1):
                cols.append(f"{res_alias}.[prev_close{i}]")
        else:
            cols.append(f"{res_alias}.[open]")
            for i in range(1, lag_degree + 1):
                cols.append(f"{res_alias}.[prev_open{i}]")

        if select_prevma:
            cols.append(f"{res_alias}.[pos_prevma]")
            cols.append(f"{res_alias}.[neg_prevma]")
        if select_prevstreak:
            cols.append(f"{res_alias}.[prev_streak]")

        cols_str = ", ".join(cols) if cols else "*"
        while True:
            with Session(self.engine) as sess:
                res = sess.execute(
                    text(
                        f"""
                        select {cols_str} from
                        (
                            select *, lag([close_pos_ma14]) over
                            (order by code asc, bar_date asc) as pos_prevma,
                            lag([close_neg_ma14]) over
                            (order by code asc, bar_date asc) as neg_prevma,
                            lag([streak]) over
                            (order by code asc, bar_date asc) as prev_streak,
                            lag([close]) over
                            (order by code asc, bar_date asc) as prev_close1,
                            lag([close], 2) over
                            (order by code asc, bar_date asc) as prev_close2,
                            lag([open]) over
                            (order by code asc, bar_date asc) as prev_open1,
                            lag([open], 2) over
                            (order by code asc, bar_date asc) as prev_open2
                            from us_daily_bars
                        ) {res_alias}
                        {filter}
                        order by code asc, bar_date asc
                        """
                    )
                )
                batch = res.fetchmany(row_cnt)
                if not batch:
                    break
                yield self.tuple_transform(batch)

    def update_ma(self, ma_lst: list, region="us"):
        """
        Keywords Arguments:
        ma_lst -- a Iterable of tuples (code, date, pos_ma, neg_ma)
        """
        keys = ["code", "bar_date", "close_pos_ma14", "close_neg_ma14"]
        set_cond = self.__format_filter_str(keys[2:], sep=",")
        where_cond = self.__format_filter_str(keys[:2], sep="and")

        with Session(self.engine) as sess:
            for i, row in enumerate(ma_lst):
                sess.execute(
                    text(
                        f"""
                    update us_daily_bars
                    set {set_cond}
                    where {where_cond}
                    """
                    ),
                    dict(zip(keys, row)),
                )
                if i % 10000 == 0:
                    sess.commit()
                    print(f"commit: {i}", end=" ", flush=True)
            sess.commit()
            print(f"finished updating {len(ma_lst)} MAs")

    def update_streaks(self, st_lst: list, region="us"):
        """
        Keywords Arguments:
        st_lst -- a Iterable of tuples (code, date, streak_count)
        """
        keys = ["code", "bar_date", "streak"]
        set_cond = self.__format_filter_str(keys[2:], sep=",")
        where_cond = self.__format_filter_str(keys[:2], sep="and")

        with Session(self.engine) as sess:
            for i, row in enumerate(st_lst):
                sess.execute(
                    text(
                        f"""
                    update us_daily_bars
                    set {set_cond}
                    where {where_cond}
                    """
                    ),
                    dict(zip(keys, row)),
                )
                if i % 10000 == 0:
                    sess.commit()
                    print(f"commit: {i}", end=" ", flush=True)
            sess.commit()
            print(f"finished updating {len(st_lst)} streaks")

    def get_last_trading_date(self, region="us"):
        assert region in ["us", "cn", "hk"], "region is invalid"
        with Session(self.engine) as sess:
            res = sess.execute(
                text(
                    f"""
                    select dbo.get_last_trading_date(:region);
                """
                ),
                {"region": region},
            ).fetchall()

        return res[0][0]

    def fetch_cal_last_date(self, region="us"):
        tname = self.__get_table_name(region=region, type="cal")
        with Session(self.engine) as sess:
            res = sess.execute(
                text(
                    f"""
                select top 1
                * from {tname}
                order by trade_date desc;
            """
                )
            ).fetchall()

        return res[0][0].strftime("%Y%m%d") if res else res

    @staticmethod
    def build_cond_str(keys, sep="and", use_null=False):
        """Get conditional SQL str"""
        assign = "is" if use_null else '='
        return f" {sep} ".join(f"{k} {assign} :{k}" for k in keys)

    @staticmethod
    def build_val_str(keys):
        """Get insert values SQL strs"""
        return ", ".join(keys), \
            ", ".join(f":{k}" for k in keys)

    def renew_calendar(self, dates: pd.DataFrame, region="us"):
        dates = dates.filter(items=["cal_date", "is_open"])
        dates.columns = ["trade_date", "is_open"]
        dates.to_sql(f"{region}_cal", con=self.engine, if_exists="append", index=False)

    def __expand_cols(self, df, cols, filter=False):
        empty_cols = set(cols) - set(df.columns)
        if len(empty_cols):
            df[list(empty_cols)] = [None] * len(empty_cols)
        if filter:
            df = df[list(cols)]
        return df

    def renew_stock_hist(self, new_df, region="us"):
        new_df = self.__expand_cols(
            new_df, _stock_table_cols["hist"][region], filter=True
        )
        assert sorted(new_df.columns) == sorted(
            _stock_table_cols["hist"]["us"]
        ), "stock hist columns invalid"
        tname = self.__get_table_name(region=region, type="hist")
        new_df.to_sql(tname, con=self.engine, if_exists="append", index=False)

    def renew_stock_list(
        self,
        new_df: pd.DataFrame,
        region="us",
    ):
        """Upsert stocks into stock list table"""

        tname = self.__get_table_name(region=region, type="lst")

        # upsert into the stock list table
        with Session(self.engine) as sess:
            for i in range(len(new_df)):
                row = new_df.iloc[i]
                params = row.to_dict()

                # update the not-null values from the new dataframe
                update_params_str = self.build_cond_str(params.keys(), sep = ",")
                res = sess.execute(
                    text(
                        f"""
                        update {tname}
                        set {update_params_str}
                        where code = :code;
                        """
                    ),
                    params,
                )

                # if no rows are updated, insert this new stock
                val_str1, val_str2 = self.build_val_str(params.keys())
                if res.rowcount == 0:
                    # insert new row
                    sess.execute(
                        text(
                            f"""
                            insert into {tname} ({val_str1})
                            values ({val_str2});
                            """
                        ),
                        params,
                    )

            sess.commit()

    def delist_stocks(self):
        with Session(self.engine) as sess:
            last_day = sess.execute(
                text(
                    """                
                    select max(trade_date)
                    from us_cal
                    """
                )
            ).fetchone()[0]

        if last_day != dt.now().date():
            print("skipping stock delisting as calendar is not up to date")
            return

        with Session(self.engine) as sess:
            res = sess.execute(text("select * from dbo.get_delisted_stocks()"))
            stocks = res.fetchall()

        if not stocks:
            return

        with Session(self.engine) as sess:
            for s in stocks:
                sess.execute(
                    text(
                        f"""
                        update us_stock_list
                        set is_delisted=1
                        where code = :code;
                        """
                    ),
                    {"code": s[1]},
                )

            sess.commit()

        print(
            f"""{len(stocks)} stocks delisted: 
            (last traded date, code, days not traded)\n""",
            stocks,
        )

    def get_stock_info(
        self,
        params={},
        only_pk=False,
        region="us",
    ):
        tname = self.__get_table_name(region=region, type="lst")
        condition_str = self.build_cond_str(params.keys(), sep="or", use_null=True)
        fetch_cols = "code" if only_pk else "*"
        with Session(self.engine) as sess:
            res = sess.execute(
                text(
                    f"""
                    select {fetch_cols} from {tname}
                    where is_delisted is 0 and ({condition_str}) 
                    """
                ),
                params,
            ).all()

        return (n[0] for n in res)

    def get_latest_bars(self):
        with Session(self.engine) as sess:
            res = sess.execute(
                text(
                    f"""
                    select * from get_all_last_dates;
                    """
                )
            ).all()

        return res
