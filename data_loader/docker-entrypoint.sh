#!/bin/sh

cd $BASE_DIR

if [ $1 = 'load' ] ; then
    echo 'Start loading...'
    pypy3 loader.py
else
    echo 'Set start mode in $1!'
    exit 1
fi
