import pandas as pd
import subprocess as sp
import os
import pickle

from sys import getsizeof
from datetime import datetime as dt, time
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import Session
from ..web_helper import ts_helper as th
from . import (
    _TRAIN_PATH,
    _hist_data_pth,
    _stock_list_pth,
    _quotes_pth,
    _timestamp_pth,
    _train_pth,
    _stock_table_cols,
)


class db_helper:
    def __connect_to_db(self, db_name):
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
        self.engine = self.__connect_to_db("detes")
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
        nullma_only=False,
        select_close=False,
        select_prevma=False,
        select_pk=False,
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

        with Session(self.engine) as sess:
            filter = ""
            res_alias = "bars_res"
            cols = []
            if nullma_only:
                filter = f"where {res_alias}.[close_pos_ma14] is NULL"
            if select_pk:
                cols.append(f"{res_alias}.[code]")
                cols.append(f"{res_alias}.[bar_date]")
            if select_close:
                cols.append(f"{res_alias}.[close]")
                cols.append(f"{res_alias}.[prev_close]")
            else:
                cols.append(f"{res_alias}.[open]")
                cols.append(f"{res_alias}.[prev_open]")

            if select_prevma:
                cols.append(f"{res_alias}.[pos_prevma]")
                cols.append(f"{res_alias}.[neg_prevma]")

            cols_str = ", ".join(cols) if cols else "*"
            res = sess.execute(
                f"""
                select {cols_str} from
                (
                    select *, lag([close_pos_ma14]) over
                    (order by code, bar_date) as pos_prevma, 
                    lag([close_neg_ma14]) over
                    (order by code, bar_date) as neg_prevma,
                    lag([close]) over
                    (order by code, bar_date) as prev_close,
                    lag([open]) over
                    (order by code, bar_date) as prev_open
                    from us_daily_bars
                ) bars_res
                {filter}
            """
            )
            rows = []
            while True:
                rows += res.fetchmany(row_cnt)
                if not rows:  # end of query
                    return

                while True:  # finish getting rows from the last code
                    next_row = res.fetchone()
                    if not next_row or next_row[0] != rows[-1][0]:
                        yield rows  # send the batch
                        rows = [next_row] if next_row else []
                        break
                    rows.append(next_row)

    def update_ma(self, ma_lst: list, region="us"):
        """
        Keywords Arguments:
        ma_df -- a Iterable of tuples (code, date, pos_ma, neg_ma)
        """
        keys = ["code", "bar_date", "close_pos_ma14", "close_neg_ma14"]
        set_cond = self.__format_filter_str(keys[2:], sep=",")
        where_cond = self.__format_filter_str(keys[:2], sep="and")

        with Session(self.engine) as sess:
            for row in iter(ma_lst):
                sess.execute(
                    f"""
                    update us_daily_bars
                    set {set_cond}
                    where {where_cond}
                    """,
                    dict(zip(keys, row)),
                )

    def get_last_trading_date(self, region="us"):
        assert region in ["us", "cn", "hk"], "region is invalid"
        with Session(self.engine) as sess:
            res = sess.execute(
                f"""
                exec get_last_trading_date @region = :region;
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
                exec get_all_last_dates;
                """
            ).all()

        return res


class cache_helper:
    def __init__(self):
        if not os.path.exists(_TRAIN_PATH):
            sp.run(f"mkdir -p {_TRAIN_PATH}", check=True, shell=True)

        self.ts_type = {
            "hist": _hist_data_pth,
            "list": _stock_list_pth,
            "quotes": _quotes_pth,
            "train": _train_pth,
        }

        # initialize tushare helper
        self.th = th()

        # initialize trade calendar
        self.calendar = self.th.get_calendar()
        self.calendar = self.calendar.set_index("cal_date").sort_index()

    def __pickle_load_all(self, pth):
        if not os.path.exists(pth):
            print(f"{pth} doesn't exist, returning empty")
            return None
        with open(pth, "rb") as f:
            while True:
                try:
                    ts = pickle.load(f)
                except EOFError:
                    return ts

    def __pickle_dump_all(self, obj, pth):
        with open(pth, "wb") as f:
            pickle.dump(obj, f)

    def cache_is_expired(self, type="hist"):
        write_pth = self.ts_type[type]
        ts = self.__pickle_load_all(_timestamp_pth)

        if write_pth not in ts:
            return True
        if type == "quotes":
            return self.__trade_is_on(timestamp=ts[write_pth]) or self.__trade_is_on(
                timestamp=dt.now()
            )
        else:
            return ts[write_pth].date() < dt.now().date()

    def cache_timestamp(self, pth):
        """
        change the pth's timestamp only, I/O bound
        """

        ts = self.__pickle_load_all(_timestamp_pth)
        if ts == None:
            ts = {}
        ts[pth] = dt.now()
        self.__pickle_dump_all(ts, _timestamp_pth)
        print(f"{pth} timestamp cached")

    def cache_data(self, df, type="quotes"):
        write_pth = self.ts_type[type]
        self.__pickle_dump_all(df, write_pth)
        self.cache_timestamp(write_pth)
        print(f"{type} cached: ", df.values.shape)

    def load_data(self, type="quotes") -> pd.DataFrame:
        read_pth = self.ts_type[type]
        df = pd.read_pickle(read_pth)  # loads the entire dataframe
        print(f"{type} loaded from cache: ", df.values.shape)
        return df

    def __trade_is_on(self, timestamp="now", ex=None) -> bool:
        """
        Trading Windows:

        # NYSE, NASDAQ: 09:30 - 16:00
        # SZSE, SHE: 09:30 - 11:30, 13:00 - 15:00
        # SEHK: 09:30 - 12:00, 13:00 - 16:00
        """
        timezones = {
            "US/Eastern": "NYSE",
            "Asia/Shanghai": "SHE",
            None: "SHE",
        }
        windows = {
            "NYSE": (time(9, 30, 0), time(16, 00, 0)),
            "SHE": (time(9, 30, 0), time(15, 0)),
            "SEHK": (time(9, 30, 0), time(16, 0)),
        }
        timestamp = dt.now() if timestamp == "now" else timestamp
        ex = ex or timezones[os.environ["TZ"]]
        if timestamp.date() < dt.now().date():
            """
            TODO: hacky logic, move this to caller
            """
            return True
        elif self.calendar.loc[dt.now().date().strftime("%Y%m%d")].is_open == 0:
            return False
        start, end = windows[ex]
        return start < timestamp.time() < end
