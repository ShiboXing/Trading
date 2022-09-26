#!/bin/bash

rm -rf build/ rumble.egg-info
pip install .
python app.py
