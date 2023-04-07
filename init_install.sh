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

### ADD GPG REPO KEYS ###

# nvidia
sudo apt-key del 7fa2af80
distribution=$(. /etc/os-release;echo $ID$VERSION_ID | sed -e 's/\.//g')
wget https://developer.download.nvidia.com/compute/cuda/repos/$distribution/x86_64/cuda-keyring_1.0-1_all.deb
sudo dpkg -i cuda-keyring_1.0-1_all.deb
rm cuda-keyring_1.0-1_all.deb*

# nvidia docker
distribution=$(. /etc/os-release;echo $ID$VERSION_ID) \
    && curl -fsSL https://nvidia.github.io/libnvidia-container/gpgkey | sudo gpg --dearmor -o /usr/share/keyrings/nvidia-container-toolkit-keyring.gpg \
    && curl -fsL https://nvidia.github.io/libnvidia-container/$distribution/libnvidia-container.list | \
        sed 's#deb https://#deb [signed-by=/usr/share/keyrings/nvidia-container-toolkit-keyring.gpg] https://#g' | \
        sudo tee /etc/apt/sources.list.d/nvidia-container-toolkit.list

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

# install other ubuntu packages
sudo apt-get remove -y docker docker-engine docker.io containerd runc
sudo ACCEPT_EULA=Y apt-get install -y \
    gnupg \
    lsb-release \
    docker-ce \
    docker-ce-cli \
    containerd.io \
    docker-buildx-plugin \
    docker-compose-plugin \
    nvidia-container-toolkit \
    msodbcsql18 \
    mssql-tools18 

# install nvidia driver
if ! nvidia-smi &> /dev/null; then
    sudo apt-get autoremove -y
    sudo apt-get purge -y *nvidia* *cuda*
    sudo apt-get install -y linux-headers-$(uname -r)
    sudo apt-get install -y nvidia-driver-525
    # need reboot
fi

# install mamba
if [ ! -d "/home/ubuntu/mambaforge" ]
then
    curl -L -o mambaforge.sh https://github.com/conda-forge/miniforge/releases/download/23.1.0-1/Mambaforge-23.1.0-1-Linux-x86_64.sh \
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
sudo nvidia-ctk runtime configure --runtime=docker
sudo pkill -9 dockerd
sudo rm -f /var/run/docker.pid
sudo dockerd & > /dev/null # run docker daemon
sleep 5
sudo chmod 666 /var/run/docker.sock
echo "=================== docker service initialization completed ==================="
docker images

# set up odbc driver
if [[ ! $PATH == *"/opt/mssql-tools18/bin"* ]];
then
    echo 'export PATH="$PATH:/opt/mssql-tools18/bin"' >> ~/.bashrc
    source ~/.bashrc
fi

# install rumble
rm -rf build/ rumble.egg-info
pip install .