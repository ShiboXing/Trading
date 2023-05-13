import pandas as pd
import os

from sys import getsizeof
from datetime import datetime as dt
from sqlalchemy import create_engine, column
from sqlalchemy.sql import text
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session
from . import _stock_table_cols


def update_rows(engine, query):
    """TODO: implement, standalone function,
    execute the write query, to be used for multiprocessing.
    map iterated rows to this SQL write function"""
    pass


class db_helper:
    __BATCH_SIZE = 1024 * 1024 * 100  # 100MB batch size

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
            connect_url,
            echo=False,
            isolation_level="READ COMMITTED",
            pool_pre_ping=True,
        )

        return engine

    def run_sqlfile(self, engine, schema_pth):
        with open(schema_pth, "r") as f:
            sql_str = f.read()
        with Session(engine.execution_options(isolation_level="SERIALIZABLE")) as sess:
            for cmd in sql_str.split("\ngo\n"):
                if cmd:
                    sess.execute(text(cmd))
                    sess.commit()


    def write_all_table_names(self, pth="db_storage/tables.txt"):
        with Session(self.engine) as sess:
            res = sess.execute(text(
                """
                SELECT [name] AS TableName
                FROM sys.tables;
                """
            ))
            table_lst = res.fetchall()
            with open(pth, 'w') as f:
                for n in table_lst: f.write(n[0] + '\n')
            

    def __init__(self, initialize_db=False):
        self.__sql_dir = os.path.join(os.path.dirname(__file__), "sql")

        # build db if needed
        if initialize_db:
            tmp_engine = self.connect_to_db(db_name="master")
            self.run_sqlfile(
                tmp_engine, os.path.join(self.__sql_dir, "schema", "build_schema.sql")
            )

            # build tables and funcs if needed
            self.engine = self.connect_to_db(db_name="detes")
            for f in sorted(os.listdir(os.path.join(self.__sql_dir, "data"))):
                self.run_sqlfile(self.engine, os.path.join(self.__sql_dir, "data", f))
        else:
            self.engine = self.connect_to_db(db_name="detes")

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

    @staticmethod
    def iter_batch(func):
        def wrapper(*args, **kwargs):
            query, engine = func(*args, **kwargs)
            with Session(engine) as sess:
                res = sess.execute(query)
                batch = res.fetchone()
                row_cnt = db_helper.__BATCH_SIZE // getsizeof(batch)

            while True:
                with Session(engine) as sess:
                    res = sess.execute(query)
                    rows = res.fetchmany(row_cnt)
                    if len(rows) == 0:
                        break
                    yield db_helper.tuple_transform(rows)

        return wrapper

    @iter_batch
    def iter_stocks_hist(
        self,
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
        return (
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
            ),
            self.engine,
        )

    def update_ma(self, ma_lst: list, region="us"):
        """
        Keywords Arguments:
        ma_lst -- a Iterable of tuples (code, date, pos_ma, neg_ma)
        """
        keys = ["code", "bar_date", "close_pos_ma14", "close_neg_ma14"]
        set_cond = self.__format_filter_str(keys[2:], sep=",")
        where_cond = self.__format_filter_str(keys[:2], sep="and")
        with Session(
            self.engine.execution_options(isolation_level="REPEATABLE READ")
        ) as sess:
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
                    print(f"{dt.now()} update_ma: commit: {i}", flush=True)
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

        with Session(
            self.engine.execution_options(isolation_level="REPEATABLE READ")
        ) as sess:
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
                    print(f"{dt.now()} update_streaks: commit: {i}", flush=True)
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
    def build_cond_str(keys, sep="and"):
        """Get conditional SQL str"""
        return f" {sep} ".join(f"{k} = :{k}" for k in keys)

    @staticmethod
    def build_val_str(keys):
        """Get insert values SQL strs"""
        return ", ".join(keys), ", ".join(f":{k}" for k in keys)

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
                update_params_str = self.build_cond_str(params.keys(), sep=",")
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
        condition_str = self.build_cond_str(params.keys(), sep="or")
        fetch_cols = "code" if only_pk else "*"
        with Session(self.engine) as sess:
            # null parameter syntax: https://learn.microsoft.com/en-us/sql/t-sql/statements/set-ansi-nulls-transact-sql?redirectedfrom=MSDN&view=sql-server-ver16
            res = sess.execute(
                text(
                    f"""
                    SET ANSI_NULLS OFF
                    select {fetch_cols} from {tname}
                    where is_delisted = 0 and ({condition_str})
                    order by code
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
