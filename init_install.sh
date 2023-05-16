#!/bin/bash

# install fundamental apt packages
sudo apt update -y 
sudo apt install -y build-essential \
    g++ \
    python3.11-dev \
    autotools-dev \
    libboost-all-dev \
    curl \
    ca-certificates 

### ADD GPG REPOS ###
# python
if [ ! -e /usr/bin/python3.11 ]; then
    sudo add-apt-repository -y ppa:deadsnakes/ppa 
fi

# nvidia
# sudo apt-key del 7fa2af80
# distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
# curl -fsSLO https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
# sudo dpkg -i cuda-keyring_1.0-1_all.deb
# rm cuda-keyring_1.0-1_all.deb*

# msft odbc
curl https://packages.microsoft.com/keys/microsoft.asc | sudo tee /etc/apt/trusted.gpg.d/microsoft.asc
curl https://packages.microsoft.com/config/ubuntu/20.04/prod.list | sudo tee /etc/apt/sources.list.d/msprod.list
sudo add-apt-repository "$(wget -qO- https://packages.microsoft.com/config/ubuntu/20.04/mssql-server-2022.list)"
sudo apt update
#########################

# install other ubuntu packages
sudo apt install -y \
    python3.11 \
    mssql-server \
    mssql-tools \
    unixodbc-dev

sudo rm -f /usr/bin/python \
    && sudo ln -s /usr/bin/python3.11 /usr/bin/python

if ! echo "$PATH" | grep -q "$HOME/.local/bin"; then
    curl https://bootstrap.pypa.io/get-pip.py | python
    echo 'export PATH="$HOME/.local/bin:$PATH"' >> ~/.bashrc
    source ~/.bashrc
fi

# set up mssql
if [[ ! $PATH == *"/opt/mssql/bin"* ]];
then
    echo 'export PATH="$PATH:/opt/mssql/bin:/opt/mssql-tools/bin/' >> ~/.bashrc
    source ~/.bashrc
    sudo /opt/mssql/bin/mssql-conf setup
    sudo systemctl start mssql-server
    sudo systemctl status mssql-server
fi

# start mssql server
if ! ps -e | grep -q "sqlservr"; then
    sudo ACCEPT_EULA=Y MSSQL_SA_PASSWORD="<YourStrong@Passw0rd>" sqlservr &
fi


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
    tushare \
    torch \
    --index-url https://download.pytorch.org/whl/cpu


# install rumble
rm -rf build/ rumble.egg-info
pip install .
