#!/bin/sh
my_date() {
    date "+%Y-%m-%d %T.%N"
}

echo "Please note only .txt and .pdf file types can be analysed by tools, \
though other file types will be downloaded from the internet archive."
fetch_collection.py $1
sqlite3 processed/hist.db "INSERT INTO History VALUES('fetch_collection', \
'"$1"', 'Finished','$(my_date)')"