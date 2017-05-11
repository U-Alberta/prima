#!/bin/sh
mkdir code
mkdir processed
mkdir source
sqlite3 processed/hist.db "CREATE TABLE History(tool text, command text, output text, time time)"
sqlite3 processed/hist.db .exit