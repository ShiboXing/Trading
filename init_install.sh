#!/bin/bash

set -e 

# install fundamental apt packages
sudo apt-get install -y build-essential \
    g++ \
    python3-dev \
    autotools-dev \
    libboost-all-dev \
    curl \
    ca-certificates 

### ADD GPG REPO KEYS ###

# nvidia
sudo apt-key del 7fa2af80
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
rm cuda-keyring_1.0-1_all.deb*

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

sudo apt-get update
#########################

# install ubuntu packages
sudo apt-get remove -y docker docker-engine docker.io containerd runc
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

# install nvidia driver
if ! nvidia-smi &> /dev/null; then
    sudo apt-get autoremove
    sudo apt-get purge -y *nvidia* *cuda*
    distribution=$(. /etc/os-release; echo $ID$VERSION_ID | sed -e 's/\.//g')
    sudo apt-get install -y linux-headers-$(uname -r)
    sudo apt-get install -y nvidia-driver-525
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
    "pandas<2.0" \
    matplotlib \
    sqlalchemy \
    pyodbc \
    pytorch \
    pytorch-cuda=11.8 \
    cuda-toolkit=11.8 \
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