#!/bin/bash

set -e

git submodule foreach git pull

# switch to storage place
pushd db_storage/Storage
git checkout -f main

# recover docker tar filesystem
git clone https://github.com/ShiboXing/Storage.git -b detes --single-branch --depth 1 
make
./deneutralizer

# deploy container 
docker_img=sql1:latest
docker import *.tar - ${docker_img}
docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=<YourStrong@Passw0rd>" \
   -p 1433:1433 --name sql1 --hostname sql1 \
   -d ${docker_img} sqlservr