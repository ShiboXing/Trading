#!/bin/bash
set -e

# hint: use /etc/odbcinst.ini on UNIX to configure driver

# clean
rm -rf build/ rumble.egg-info

# compile 
pip install .