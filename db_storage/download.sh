#!/bin/bash

# 
pushd Storage
git checkout -f detes
docker export sql1 > latest.tar
ls -alh latest.tar
