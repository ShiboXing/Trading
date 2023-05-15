#!/bin/bash

# install fundamental apt packages
sudo apt-get update -y 
sudo apt-get install -y build-essential \
    g++ \
    python3-dev \
    autotools-dev \
    libboost-all-dev \
    curl \
    ca-certificates 

### ADD GPG REPOS ###
# python
sudo add-apt-repository ppa:deadsnakes/ppa 

# nvidia
# sudo apt-key del 7fa2af80
# distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
# curl -fsSLO https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
# sudo dpkg -i cuda-keyring_1.0-1_all.deb
# rm cuda-keyring_1.0-1_all.deb*

# msft odbc
curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/ubuntu/20.04/mssql-server-2022.list)"
sudo apt-get update
#########################

# install other ubuntu packages
sudo ACCEPT_EULA=Yes apt-get install \
    python3.11 \
    python3-pip \
    mssql-tools \
    unixodbc-dev 
    # mssql-server \

sudo rm /usr/bin/python \
    && sudo ln -s /usr/bin/python3.11 /usr/bin/python

# if lspci | grep -i NVIDIA &>/dev/null; then
# 	sudo apt-get install -y nvidia-container-toolkit
# fi

# install nvidia driver
# if (lspci | grep -i NVIDIA) && ! nvidia-smi &>/dev/null; then
#     echo "NVIDIA GPU exists but nvidia-smi doesn't work"
#     sudo apt-get autoremove -y
#     sudo apt-get purge -y *nvidia* *cuda*
#     sudo apt-get install -y linux-headers-$(uname -r)
#     sudo apt-get install -y nvidia-driver-525
#     # need reboot
# fi

# install python packages
pip install \
    ipython \
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
if [[ ! $PATH == *"/opt/mssql-tools18/bin"* ]];
then
    echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
    source ~/.bashrc
fi

# install rumble
rm -rf build/ rumble.egg-info
pip install .
