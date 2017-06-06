#!/bin/sh
mkdir workspace
cd "${0%/*}"
cd ../src
make clean
make