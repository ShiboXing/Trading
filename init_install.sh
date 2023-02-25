#!/bin/bash

# install devtoolset
sudo apt-get install build-essential \
    g++ \
    python3-dev \
    autotools-dev \
    libcu-dev \
    libbz2-d2v \
    libboost-all-dev \
    devtoolset-10

# install c++ boost library
wget https://boostorg.jfrog.io/artifactory/main/release/1.81.0/source/boost_1_81_0.tar.gz \
    && tar xvf boost_1_81_0.tar.gz \
    && pushd boost_1_81_0 \
    && ./bootstrap.sh --prefix=/usr/ \
    && sudo ./b2 install \
    && popd \
    && rm -rf boost_1_81_0.tar.gz boost_1_81_0
    
# install python packages
mamba install ipdb \
    black \
    yfinance \
    numpy \
    pytorch \
    torchvision \
    torchaudio \
    pytorch-cuda=11.7 \
    -c pytorch \
    -c nvidia

pip install jupyterlab notebook yahooquery

