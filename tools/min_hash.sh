#!/bin/sh
echo "gcc -shared -fPIC -I/usr/include/python2.7/ -lpython2.7 -o minHash.so minHash.c"
min_hash.py