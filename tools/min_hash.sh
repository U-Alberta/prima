#!/bin/sh
echo "gcc sqlite3.c -o minHash minHash.c -lpthread -ldl"
echo "gcc -shared -fPIC -I/usr/include/python2.7/ -lpython2.7 -o minHash.so pythonModule.c"
min_hash.py