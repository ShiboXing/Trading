import pandas as pd
import subprocess as sp
import os
import pickle

from datetime import datetime as dt, time
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL, Engine
from sqlalchemy.orm import Session
from ..tushare_helper import ts_helper as th
from . import (
    _TRAIN_PATH,
    _hist_data_pth,
    _stock_list_pth,
    _quotes_pth,
    _timestamp_pth,
    _train_pth,
    _stock_list_cols,
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
            conn.execute(sql_str)
            conn.commit()

    def __init__(self):
        self.__file_dir__ = os.path.dirname(__file__)
        self.__schema_script__ = ""
        tmp_engine = self.__connect_to_db("master")
        self.__run_sqlfile(tmp_engine, "build_schema.sql")
        self.engine = self.__connect_to_db("detes")
        self.__run_sqlfile(self.engine, "build_tables.sql")

    def __get_table_name(self, region="us", type="lst"):
        assert region in ("us", "cn", "hk"), "region parameter is incorrect"
        assert type in ("lst", "cal"), "table type parameter is incorrect"
        if type == "lst":
            return f"{region}_stock_list"
        elif type == "cal":
            return f"{region}_cal"

    def fetch_cal_last_date(self, region="us"):
        tname = self.__get_table_name(region=region, type="cal")
        with self.engine.connect() as conn:
            query = f"""
                select top 1
                * from {tname}
                order by trade_date desc;
            """
            res = conn.execute(query)
            res = res.fetchall()

        return res[0][0].strftime("%Y%m%d") if res else res

    @staticmethod
    def build_cond_args(params):
        conditions = []
        for k, v in params.items():
            if v is None:
                conditions.append(f"{k} is null")
            else:
                conditions.append(f"{k} = :{k}")
        return " and ".join(conditions)

    def renew_calendar(self, dates: pd.DataFrame, region="us"):
        dates = dates.filter(items=["cal_date", "is_open"])
        dates.columns = ["trade_date", "is_open"]
        dates.to_sql(f"{region}_cal", con=self.engine, if_exists="append", index=False)

    def renew_stock_list(
        self,
        new_df: pd.DataFrame,
        region="us",
    ):

        tname = self.__get_table_name(region=region, type="lst")
        assert sorted(list(new_df.columns)) == sorted(
            list(_stock_list_cols[region])
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
            set(_stock_list_cols[region])
        ), f"column parameters have conflicts with {tname}"

        condition_str = self.build_cond_args(params)
        limit_str = f"top {limit}" if limit else ""

        fetch_cols = "code" if only_pk else "*"
        with Session(self.engine) as sess:
            res = sess.execute(
                f"""
                select {limit_str} {fetch_cols} from {tname}
                where {condition_str};
            """,
                params,
            ).all()

        return (n[0] for n in res)

    def get_stock_hist(self, params={}, only_pk=True):
        pass


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
