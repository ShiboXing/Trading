#!/bin/bash

set -e 

# install fundamental apt packages
apt-get install -y build-essential \
    g++ \
    python3-dev \
    autotools-dev \
    libboost-all-dev \
    curl \
    ca-certificates 

### ADD GPG REPO KEYS ###

# nvidia
sudo apt-key del 7fa2af80
source /etc/os-release
distro=$ID`lsb_release -rs | sed 's/\.//'`; arch=$(uname -m); curl -o nvidia-keyring.deb -L https://developer.download.nvidia.com/compute/cuda/repos/$distro/$arch/cuda-keyring_1.0-1_all.deb
sudo dpkg -i nvidia-keyring.deb
rm nvidia-keyring.deb
sudo apt-get update

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

#########################

# install ubuntu packages
sudo apt-get update
sudo apt-get remove docker docker-engine docker.io containerd runc
sudo ACCEPT_EULA=Y apt-get install -y build-essential \
    g++ \
    python3-dev \
    autotools-dev \
    libboost-all-dev \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin \
    msodbcsql18 \
    mssql-tools18 

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

# reinstall cuda driver and toolkit
# sudo /usr/local/cuda-11.8/bin/cuda-uninstaller | true
sudo apt-get autoremove
sudo apt-get purge -y *nvidia* *cuda*
wget https://developer.download.nvidia.com/compute/cuda/11.8.0/local_installers/cuda_11.8.0_520.61.05_linux.run
sudo sh cuda_11.8.0_520.61.05_linux.run --silent
rm cuda_11.8.0_520.61.05_linux.run
export CUDA_HOME=/usr/local/cuda
sudo apt-get install -y cuda-cudart-11-8
    
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
    pytorch-cuda=11.8 \
    -c pytorch \
    -c nvidia
pip install jupyterlab notebook yahooquery tushare

# start servives
if [ -z "$(ps -e | grep dockerd)" ];
then
    sudo pkill -9 dockerd
    sudo rm -f /var/run/docker.pid
    sudo chmod 666 /var/run/docker.sock 
    sudo dockerd & > /dev/null # run docker daemon
    sleep 5
    echo "=================== docker service initialization completed ==================="
    docker images
fi

# set up odbc driver
if [[ ! $PATH == *"/opt/mssql-tools18/bin"* ]];
then
    echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
    source ~/.bashrc
fi

# install rumble
rm -rf build/ rumble.egg-info
pip install .