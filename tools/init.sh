#!/bin/sh
mkdir code
mkdir processed
mkdir source
sqlite3 processed/hist.db "CREATE TABLE History(command text, output text)"
sqlite3 processed/hist.db .exit