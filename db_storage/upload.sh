#!/bin/bash

set -e

git submodule update --init --recursive

# write to disk 
pushd db_storage/Storage
git clone https://github.com/ShiboXing/Storage -b detes --single-branch --depth 1
pushd Storage
git checkout -f detes
rm part_*
docker export sql1 > latest.tar
ls -ahl latest.tar

# discretize
popd
make
./neutralizer Storage
rm Storage/latest.tar

# upload
pushd Storage
echo "git ops start"
git add .
git commit -m "latest"
git push origin detes
popd

# free filesystem
rm -r Storage
popd