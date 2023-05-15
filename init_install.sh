#!/bin/bash

# install fundamental apt packages
sudo apt-get update -y 
sudo apt-get install -y build-essential \
    g++ \
    python3-dev \
    autotools-dev \
    libboost-all-dev \
    curl \
    ca-certificates \
    python3.11 \
    python3-pip
     
### ADD GPG REPO KEYS ###

# nvidia
# sudo apt-key del 7fa2af80
# distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
# curl -fsSLO https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
# sudo dpkg -i cuda-keyring_1.0-1_all.deb
# rm cuda-keyring_1.0-1_all.deb*

# msft odbc
sudo curl -fsSL https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --batch --yes --dearmor -o /etc/apt/keyrings/mssql.gpg
echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/mssql.gpg] https://packages.microsoft.com/ubuntu/22.04/prod \
    $(lsb_release -cs) main" \ | sudo tee /etc/apt/sources.list.d/mssql-release.list > /dev/null

sudo apt-get update
#########################

# install other ubuntu packages
# sudo apt-get install \
#     msodbcsql18 \
#     mssql-tools18 

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
    ipdb \
    black \
    yfinance \
    numpy \
    pandas \
    matplotlib \
    sqlalchemy \
    pyodbc \
    torch \
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
