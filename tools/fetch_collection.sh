#!/bin/sh
my_date() {
	date "+%Y-%m-%d %T.%N"
}

echo "Please note only .txt and .pdf file types can be analysed by tools."
fetch_collection.py $1
sqlite3 processed/hist.db "INSERT INTO History VALUES('fetch_collection', '"$1"', 'True','$(my_date)')"