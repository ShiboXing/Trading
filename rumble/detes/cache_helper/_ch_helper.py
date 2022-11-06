import pandas as pd
import subprocess as sp
import os
import pyodbc
import pickle

from datetime import datetime as dt, time
from sqlalchemy import create_engine
from sqlalchemy.engine import URL
from ..tushare_helper import ts_helper as th
from . import (
    _TRAIN_PATH,
    _hist_data_pth,
    _stock_list_pth,
    _quotes_pth,
    _timestamp_pth,
    _train_pth,
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
                driver="ODBC Driver 18 for SQL Server",
                TrustServerCertificate="yes",
            ),
        )

        engine = create_engine(
            connect_url,
            echo=False,
        )

        return engine

    def __build_schemas(self, conn):
        schema_pth = os.path.join(self.__file_dir__, "db", "schema.sql")
        cur = conn.cursor()
        with open(schema_pth, "r") as f:
            sql_str = f.read()

        cur.execute(sql_str)
        cur.commit()

    def __init__(self):
        self.__file_dir__ = os.path.dirname(__file__)
        self.__schema_script__ = ""
        tmp_engine = self.__connect_to_db("master")
        self.__build_schemas(tmp_engine)
        self.engine = self.__connect_to_db("detes")

    def fetch_last_date(self, region="us"):
        cur = self.engine.cursor()
        query = f"""
            select top 1
            * from {region}_cal 
            order by trade_date desc;
        """
        cur.execute(query)
        res = cur.fetchall()

        return res[0] if res else res

    def renew_calendar(self, dates: pd.DataFrame, region="us"):
        dates.columns = ["trade_date", "is_open"]
        dates.to_sql(f"{region}_cal", con=self.engine, if_exists="append")


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
