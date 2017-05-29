#!/bin/sh
gcc -o minHash minHash.c sqlite3.c -lpthread -ldl
gcc -shared -fPIC -I/usr/include/python2.7/ -lpython2.7 -o minHash.so minHashModule.c sqlite3.c -lpthread -ldl

min_hash.py