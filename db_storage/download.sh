#!/bin/bash

set -e

# switch to storage place
pushd db_storage
git clone https://github.com/ShiboXing/Storage -b main --single-branch --depth 1


   # recover docker tar filesystem   
   pushd Storage
   git clone https://github.com/ShiboXing/Storage.git -b detes --single-branch --depth 1 
   make
   ./deneutralizer Storage

   # deploy container 
   tag="latest"
   docker_img="sql1:${tag}"
   cat "Storage/${tag}.tar" | docker import - ${docker_img}
   docker run -e "ACCEPT_EULA=Y" -e "MSSQL_SA_PASSWORD=<YourStrong@Passw0rd>" \
      -p 1433:1433 --name sql1 --hostname sql1 \
      -d ${docker_img} "/opt/mssql/bin/sqlservr"

   docker exec sql1 /opt/mssql-tools/bin/sqlcmd \
   -S localhost -U SA -P '<YourStrong@Passw0rd>' \
   -Q 'SELECT @@VERSION'
   popd

# free the filesystem
rm -rf Storage
popd