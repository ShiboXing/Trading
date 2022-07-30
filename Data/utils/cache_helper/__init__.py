import os
import subprocess as sp


CACHE_PATH = os.path.expanduser("~/.trading_data")
class cache:    
    def __init__(self):
        if not os.path.exists(CACHE_PATH):
            sp.run(f"mkdir -p {CACHE_PATH}", check=True, shell=True)
    