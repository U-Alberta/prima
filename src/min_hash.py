#!/usr/bin/python
import _minHash
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
import shared
import sqlite3
import sys

MINHASHFOLDER = "processed/min_hash/"
SHINGLEDB = "processed/shingles.db"

def min_hash():
    if len(sys.argv) == 1:
        args = ""
        k = 3
        hashes = 200
    elif len(sys.argv) == 3:
        args = " ".join(sys.argv[1:])
        k = int(sys.argv[1])
        hashes = int(sys.argv[2])
    else:
        shared.error("11", ["min_hash", ""])
        return -1
    conn = sqlite3.connect(SHINGLEDB)
    c = conn.cursor()
    c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name="\
        "'Shingle'")
    if c.fetchone() == None:
        try:
            shingles, docs = shared.gen_shingles(k)
        except:
            shared.error("6", ["min_hash", args], k)
            return -1
        try:
            insert_shingles(shingles, docs)
        except:
            shared.error("9", ["min_hash", args], SHINGLEDB)
            return -1
    try:
        if not os.path.exists(MINHASHFOLDER):
            os.makedirs(MINHASHFOLDER)
        _minHash.minHash(hashes)
    except:
        shared.error("2", ["min_hash", args])
        return -1
    try:
        shared.insert_to_db("min_hash", args, "Finished")
    except:
        shared.error("10", ["min_hash", args])
        return -1
    return 1

"""
Save the k-shingles to a database to be accessed in the c program

params: shingles (created by shared.gen_shingles)
return:
"""
def insert_shingles(shingles, documents):
    conn = sqlite3.connect(SHINGLEDB)
    c = conn.cursor()
    for i in range(0, len(documents)):
        documents[i] = (i, documents[i])
    c.execute("CREATE TABLE Shingle(docid int, shingle text)")
    conn.commit()
    c.executemany("INSERT INTO Shingle VALUES(?,?)", shingles)
    conn.commit()
    c.execute("CREATE TABLE Document(docid int, docname text)")
    conn.commit()
    c.executemany("INSERT INTO Document VALUES(?,?)", documents)
    conn.commit()
    conn.close()
    return 1

if __name__ == '__main__':
    min_hash()