#!/bin/bash
set -e

# link mssql drivers properly on MAC
# mkdir -p /usr/local/bin/odbcinst/
# sudo ln -sf /usr/local/bin/odbcinst/odbcinst.ini /etc/odbcinst.ini
# sudo ln -sf /usr/local/bin/odbcinst/odbc.ini /etc/odbc.ini

# clean
rm -rf build/ rumble.egg-info

# compile 
pip install .