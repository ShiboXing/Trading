#!/bin/bash

# write to disk 
pushd Storage
git checkout -f detes
docker export sql1 > latest.tar
ls -alh latest.tar

# discretize
git clone https://github.com/ShiboXing/Storage.git -b main --single-branch --depth 1 
pushd Storage
make
./neutralizer
popd

# upload
rm -rf Storage
git add .
git commit -m "latest"
git push origin detes
popd
