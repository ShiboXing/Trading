#!/bin/bash
set -e

# clean
rm -rf build/ rumble.egg-info

# compile 
pip install .

# run
python app.py
