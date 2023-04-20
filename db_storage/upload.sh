#!/bin/bash

set -e

pushd db_storage

# write to disk 
pushd Storage
git clone https://github.com/ShiboXing/Storage -b detes --single-branch --depth 1

    # export docker
    pushd Storage
    git checkout -f detes
    rm part_*
    docker export sql1 > latest.tar
    ls -ahl latest.tar
    popd

    # discretize
    make
    ./neutralizer Storage
    rm -f Storage/latest.tar

    # upload
    pushd Storage
    echo "git ops start"
    git add .
    git commit -m "latest"
    git push origin detes
    popd

# free filesystem
rm -rf Storage
popd