#!/bin/sh
my_date() {
	date "+%Y-%m-%d %T.%N"
}
ia download --search "collection:"$1 --destdir=source
sqlite3 processed/hist.db "INSERT INTO History VALUES('fetch_collection', '"$1"', 'True','$(my_date)')"