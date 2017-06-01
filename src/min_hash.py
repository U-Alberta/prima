#!/usr/bin/python
import ctypes
import glob
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
import sqlite3
import sys

MINHASHFOLDER = "processed/min_hash"
SHINGLEDB = "processed/shingles.db"

def min_hash():
	if len(sys.argv) != 1:
		glob.error("17", ["min_hash", ""])
		return -1
	try:
		shingles = glob.gen_shingles()
	except:
		glob.error("10", ["min_hash", "", glob.SHINGLES])
		return -1
	try:
		insert_shingles(shingles)
	except:
		glob.error("15", ["min_hash", "", SHINGLESDB])
		return -1
	try:
		if not os.path.exists(MINHASHFOLDER):
			os.makedirs(MINHASHFOLDER)
		call_c()
	except:
		glob.error("2", ["min_hash", ""])
		return -1
	try:
		glob.insert_to_db("min_hash", "", "Finished")
	except:
		glob.error("16", ["min_hash", ""])
		return -1
	return 1

"""
Save the k-shingles to a database to be accessed in the c program
"""
# TODO: keep this db? (right now it's kept)
def insert_shingles(shingles):
	conn = sqlite3.connect(SHINGLEDB)
	c = conn.cursor()
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name="\
		"'Shingle'")
	if c.fetchone() != None:
		c.execute("DROP TABLE Shingle")
		conn.commit()
	c.execute("CREATE TABLE Shingle(docid int, docname text, shingle text)")
	conn.commit()
	c.executemany("INSERT INTO Shingle VALUES(?,?,?)", shingles)
	conn.commit()
	conn.close()
	return 1

"""
Call the c file to do the expensive functions for hashing
"""
def call_c():
	temp = os.path.abspath(__file__)
	temp = os.path.realpath(temp)
	temp = os.path.dirname(temp)
	path = os.path.join(temp, "minHash.so")
	testlib = ctypes.CDLL(path)
	testlib.callMinHash()
	return 1

min_hash()