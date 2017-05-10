#!/bin/sh
mkdir code
mkdir processed
mkdir source
sqlite3 processed/hist.db "CREATE TABLE History(tool text, command text, output text, time time)"
sqlite3 processed/hist.db .exit
sqlite3 processed/inverted_index.db "CREATE TABLE Token(token text, df int, token_id int PRIMARY KEY)"
sqlite3 processed/inverted_index.db "CREATE TABLE Posting(token_id int, doc_id int, offset int, tf int, tf_idf float)"
sqlite3 processed.inverted_index.db .exit