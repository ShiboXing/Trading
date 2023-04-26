import time, os, argparse
import torch

from rumble.detes import fetcher
from rumble.detes._loader import TechBuilder
from rumble.rumble.tech.domains import Domains
from multiprocessing import Pool, cpu_count


def __update_agg(args):
    """Update single row where agg data is unfilled till there are no more such rows"""
    is_industry, rank = args
    os.environ["RANK"] = str(rank % 4)
    d = Domains()
    row_cnt = 0
    while d.update_agg_signals(is_industry=is_industry):
        row_cnt += 1

    print(f"pid {os.getpid()} finished updating {row_cnt} rows")


if __name__ == "__main__":
    """Just Die"""
    parser = argparse.ArgumentParser(description="specify the arguments of detes app")
    parser.add_argument(
        "--init", help="initialize the database/schema", action="store_true"
    )
    parser.add_argument("--hist", help="update history price", action="store_true")
    parser.add_argument("--list", help="update stock list", action="store_true")
    parser.add_argument(
        "--ma", help="update moving average signals", action="store_true"
    )
    parser.add_argument(
        "--streak", help="update daily streak signals", action="store_true"
    )
    parser.add_argument(
        "--industry", help="update industry signals", action="store_true"
    )
    parser.add_argument("--sector", help="update sector signals", action="store_true")
    args = parser.parse_args()
    # os.environ["TZ"] = "Asia/Shanghai"
    os.environ["TZ"] = "US/Eastern"
    time.tzset()
    
    # create all sql objects, re-define funcs, procs and views
    if args.init:
        Domains(initialize_db=True)

    ft = fetcher("20000101", "us")
    if args.list:
        ft.update_us_stock_lst()  # weekly task
    if args.hist:
        ft.update_cal()
        ft.update_stock_hist()

    tb = TechBuilder()
    if args.ma:
        tb.update_ma()
    if args.streak:
        tb.update_streaks()

    if args.industry or args.sector:
        d = Domains()
        d.update_agg_dates(is_industry=True)
        d.update_agg_dates(is_industry=False)
        del d
        nproc = cpu_count()
        print("nproc: ", nproc, flush=True)
        with Pool(nproc) as pool:
            for res in pool.imap_unordered(
                __update_agg, [(args.industry, i) for i in range(nproc)]
            ):
                pass

    # index_rets = d.get_index_rets("2023-01-03", "2023-02-03")
