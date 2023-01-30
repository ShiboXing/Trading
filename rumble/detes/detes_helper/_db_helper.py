import pandas as pd
import os

from sys import getsizeof
from datetime import datetime as dt
from sqlalchemy import create_engine
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

    def __connect_to_db(self, db_name="detes"):
        creds_pth = os.path.join(self.__file_dir__, "db", ".sql_creds")
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

    def __run_sqlfile(self, engine, fname):
        schema_pth = os.path.join(self.__file_dir__, "db", fname)
        with Session(engine) as sess:
            conn = engine.raw_connection()
            with open(schema_pth, "r") as f:
                sql_str = f.read()
            for cmd in sql_str.split("\ngo\n"):
                if cmd:
                    conn.execute(cmd)
                    conn.commit()

    def __init__(self):
        self.__file_dir__ = os.path.dirname(__file__)
        self.__schema_script__ = ""
        tmp_engine = self.__connect_to_db("master")
        self.__run_sqlfile(tmp_engine, "build_schema.sql")
        self.engine = self.__connect_to_db()
        self.__run_sqlfile(self.engine, "build_tables.sql")
        self.__run_sqlfile(self.engine, "build_funcs.sql")

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
        get previous moving average in every row
        """
        batch_size = 1024 * 1024 * 100  # 100MB batch size
        row_cnt = 0

        # get row count in each batch based row mem size
        with Session(self.engine) as sess:
            first_row = sess.execute(
                f"""
                select top 1 * from us_daily_bars
                """
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
                batch = res.fetchmany(row_cnt)
                if not batch: break
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
                    f"""
                    update us_daily_bars
                    set {set_cond}
                    where {where_cond}
                    """,
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
                    f"""
                    update us_daily_bars
                    set {set_cond}
                    where {where_cond}
                    """,
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
                f"""
                    select dbo.get_last_trading_date(:region);
                """,
                {"region": region},
            ).fetchall()

        return res[0][0]

    def fetch_cal_last_date(self, region="us"):
        tname = self.__get_table_name(region=region, type="cal")
        with Session(self.engine) as sess:
            res = sess.execute(
                f"""
                select top 1
                * from {tname}
                order by trade_date desc;
            """
            ).fetchall()

        return res[0][0].strftime("%Y%m%d") if res else res

    @staticmethod
    def build_cond_args(params):
        conditions = []
        if not params:
            return ""
        for k, v in params.items():
            if v is None:
                conditions.append(f"{k} is null")
            else:
                conditions.append(f"{k} = :{k}")
        return "where " + " and ".join(conditions)

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
        _us_stock_list_cols = _stock_table_cols["list"][region]
        new_df = self.__expand_cols(new_df, _us_stock_list_cols)
        tname = self.__get_table_name(region=region, type="lst")
        assert sorted(list(new_df.columns)) == sorted(
            list(_us_stock_list_cols)
        ), f"column parameters have conflicts with {tname}"

        # upsert into the stock list table
        with Session(self.engine) as sess:
            for i in range(len(new_df)):
                row = new_df.iloc[i]
                params = row.to_dict()

                # update the not-null values from the new dataframe
                update_params = []
                insert_cols = []
                insert_params = []
                for k, v in params.items():
                    if v != None:
                        if update_params:
                            update_params.append(", ")
                            insert_cols.append(", ")
                            insert_params.append(", ")
                        update_params.append(f"{k} = :{k}")
                        insert_cols.append(k)
                        insert_params.append(f":{k}")
                update_params_str = "".join(update_params)
                insert_cols_str = "".join(insert_cols)
                insert_params_str = "".join(insert_params)
                res = sess.execute(
                    f"""
                    update {tname}
                    set {update_params_str}
                    where code = :code;
                """,
                    params,
                )

                # if no rows are updated, insert this new stock
                if res.rowcount == 0:
                    # insert new row
                    sess.execute(
                        f"""
                        insert into {tname} ({insert_cols_str})
                        values ({insert_params_str});
                        """,
                        params,
                    )

            sess.commit()

    def delist_stocks(self):    
        with Session(self.engine) as sess:
            last_day = sess.execute("""                
                select max(trade_date)
                from us_cal
            """).fetchone()[0]

        if last_day != dt.now().date():
            print("skipping stock delisting as calendar is not up to date")
            return
            
        with Session(self.engine) as sess:
            res = sess.execute("select * from dbo.get_delisted_stocks()")
            stocks = res.fetchall()

        if not stocks:
            return

        with Session(self.engine) as sess:
            filter = "code"
            for s in stocks:
                sess.execute(f"""
                    update us_stock_list
                    set is_delisted=1
                    where {filter} = :{filter};
                """, {filter: s[1]})
            sess.commit()
            
        print("""stocks delisted: 
            (last traded date, code, days not traded)\n""", stocks)


    def get_stock_info(
        self,
        params={},
        only_pk=False,
        limit: int or None = None,
        region="us",
    ):
        tname = self.__get_table_name(region=region, type="lst")
        assert set(params.keys()).issubset(
            set(_stock_table_cols["list"][region])
        ), f"column parameters have conflicts with {tname}"

        condition_str = self.build_cond_args(params)
        limit_str = f"top {limit}" if limit else ""
        fetch_cols = "code" if only_pk else "*"
        with Session(self.engine) as sess:
            res = sess.execute(
                f"""
                select {limit_str} {fetch_cols} from {tname}
                {condition_str};
            """,
                params,
            ).all()

        return (n[0] for n in res)

    def get_stock_hist(
        self, params={}, limit: int or None = None, only_pk=True, region="us"
    ):
        tname = self.__get_table_name(region=region, type="hist")
        assert set(params.keys()).issubset(
            set(_stock_table_cols["hist"][region])
        ), f"column parameters have conflicts with {tname}"
        condition_str = self.build_cond_args(params)
        limit_str = f"top {limit}" if limit else ""

        fetch_cols = "code" if only_pk else "*"
        with Session(self.engine) as sess:
            res = sess.execute(
                f"""
                select {limit_str} {fetch_cols} from {tname}
                {condition_str};
            """,
                params,
            ).all()

        return (n[0] for n in res)

    def get_latest_bars(self):
        with Session(self.engine) as sess:
            res = sess.execute(
                f"""
                select * from get_all_last_dates;
                """
            ).all()

        return res