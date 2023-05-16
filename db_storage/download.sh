#!/bin/bash

set -e

python detes_app.py --init
# switch to storage place
pushd db_storage

   # clone the utils
   git clone https://github.com/ShiboXing/Storage.git -b detes --single-branch --depth 1 storage

   # clone data
   git clone https://github.com/ShiboXing/Storage.git -b main --single-branch --depth 1 storage_utils
   pushd storage_utils
   make
   ./deneutralizer ../storage
   popd
popd

# insert data into sql server
python detes_app.py --load-tables
