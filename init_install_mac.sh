#!/bin/bash

# install fundamental brew packages
brew install python boost

# install python packages
pip install \
    ipdb \
    black \
    yfinance \
    numpy \
    pandas \
    matplotlib \
    sqlalchemy \
    pyodbc \
    jupyterlab \
    notebook \
    yahooquery \
    tushare

# set up odbc driver
/bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
brew tap microsoft/mssql-release https://github.com/Microsoft/homebrew-mssql-release
brew update
HOMEBREW_ACCEPT_EULA=Y brew install msodbcsql18 mssql-tools18

# install rumble
rm -rf build/ rumble.egg-info
pip install .