#!/bin/bash

set -e 

### ADD GPG REPO KEYS ###

# nvidia
sudo apt-key del 7fa2af80
source /etc/os-release
distro=$ID`lsb_release -rs | sed 's/\.//'`; arch=$(uname -m); curl -o nvidia-keyring.deb -L https://developer.download.nvidia.com/compute/cuda/repos/$distro/$arch/cuda-keyring_1.0-1_all.deb
sudo dpkg -i nvidia-keyring.deb
rm nvidia-keyring.deb

# docker
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --batch --yes --dearmor -o /etc/apt/keyrings/docker.gpg
echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/ubuntu \
    $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# msft odbc
sudo curl https://packages.microsoft.com/keys/microsoft.asc | sudo gpg --batch --yes --dearmor -o /etc/apt/keyrings/mssql.gpg
echo \
    "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/mssql.gpg] https://packages.microsoft.com/ubuntu/22.04/prod \
    $(lsb_release -cs) main" \ | sudo tee /etc/apt/sources.list.d/mssql-release.list > /dev/null

# install ubuntu packages
sudo apt-get update
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo ACCEPT_EULA=Y apt-get install -y build-essential \
    g++ \
    python3-dev \
    autotools-dev \
    libboost-all-dev \
    ca-certificates \
    gnupg \
    lsb-release \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin \
    msodbcsql18 \
    mssql-tools18 \
    nvidia-driver-525 \
    cuda-drivers-fabricmanager-525

# install cuda toolkit
if [ -z "$(apt list --installed | grep cuda)" ];
then
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2204/x86_64/cuda-ubuntu2204.pin
    sudo mv cuda-ubuntu2204.pin /etc/apt/preferences.d/cuda-repository-pin-600
    wget https://developer.download.nvidia.com/compute/cuda/12.0.1/local_installers/cuda-repo-ubuntu2204-12-0-local_12.0.1-525.85.12-1_amd64.deb
    sudo dpkg -i cuda-repo-ubuntu2204-12-0-local_12.0.1-525.85.12-1_amd64.deb
    sudo cp /var/cuda-repo-ubuntu2204-12-0-local/cuda-*-keyring.gpg /usr/share/keyrings/
    sudo apt-get update
    sudo apt-get install -y cuda
fi

# install c++ boost library
if [ ! -d "/usr/include/boost" ]
then
    wget https://boostorg.jfrog.io/artifactory/main/release/1.81.0/source/boost_1_81_0.tar.gz \
        && tar xvf boost_1_81_0.tar.gz \
        && pushd boost_1_81_0 \
        && ./bootstrap.sh --prefix=/usr/ \
        && sudo ./b2 install \
        && popd \
        && sudo rm -rf boost_1_81_0.tar.gz boost_1_81_0
fi
    
# install mamba
if [ ! -d "/home/ubuntu/mambaforge" ]
then
    curl -L -o mambaforge.sh https://github.com/conda-forge/miniforge/releases/download/22.11.1-4/Mambaforge-22.11.1-4-Linux-x86_64.sh \
        && bash mambaforge.sh -b -u \
        && rm mambaforge.sh \
        && /home/ubuntu/mambaforge/bin/mamba init \
        && source ~/.bashrc
fi

# install python packages
mamba install -y \
    python=3.10 \
    ipdb \
    black \
    yfinance \
    numpy \
    pandas \
    matplotlib \
    sqlalchemy \
    pyodbc \
    pytorch \
    pytorch-cuda=11.7 \
    -c pytorch \
    -c nvidia
pip install jupyterlab notebook yahooquery tushare

# install rumble
rm -rf build/ rumble.egg-info
pip install .

# start servives
if [ -z "$(ps -e | grep dockerd)" ];
then
    sudo systemctl stop docker
    rm -f /var/run/docker.pid
    sudo groupadd docker | true
    newgrp docker
    sudo dockerd & # run docker daemon
    sudo chmod 666 /var/run/docker.sock 
    docker images
fi

# set up odbc driver
if [[ ! $PATH == *"/opt/mssql-tools18/bin"* ]];
then
    echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
    source ~/.bashrc
fi
