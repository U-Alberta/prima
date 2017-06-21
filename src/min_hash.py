#!/usr/bin/python
<<<<<<< HEAD
import _minHash
=======
import ctypes
>>>>>>> 15d648cbfdb5aec698ff3667d6e94a5147f5613a
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
import shared
import sqlite3
import sys

MINHASHFOLDER = "processed/min_hash/"
SHINGLEDB = "processed/shingles.db"

def min_hash():
<<<<<<< HEAD
	if len(sys.argv) == 1:
		args = ""
		k = 3
		hashes = 200
	elif len(sys.argv) == 3:
		args = " ".join(sys.argv[1:])
		k = int(sys.argv[1])
		hashes = int(sys.argv[2])
	else:
=======
	if len(sys.argv) != 1:
>>>>>>> 15d648cbfdb5aec698ff3667d6e94a5147f5613a
		shared.error("11", ["min_hash", ""])
		return -1
	conn = sqlite3.connect(SHINGLEDB)
	c = conn.cursor()
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name="\
		"'Shingle'")
	if c.fetchone() == None:
		try:
<<<<<<< HEAD
			shingles, docs = shared.gen_shingles(k)
		except:
			shared.error("6", ["min_hash", args], k)
=======
			shingles, docs = shared.gen_shingles()
		except:
			shared.error("6", ["min_hash", ""])
>>>>>>> 15d648cbfdb5aec698ff3667d6e94a5147f5613a
			return -1
		try:
			insert_shingles(shingles, docs)
		except:
<<<<<<< HEAD
			shared.error("9", ["min_hash", args], SHINGLEDB)
			return -1
	#try:
	if not os.path.exists(MINHASHFOLDER):
		os.makedirs(MINHASHFOLDER)
	_minHash.minHash(hashes)
	"""
	except:
		shared.error("2", ["min_hash", args])
		return -1
	"""
	try:
		shared.insert_to_db("min_hash", args, "Finished")
	except:
		shared.error("10", ["min_hash", args])
=======
			shared.error("9", ["min_hash", ""], SHINGLEDB)
			return -1
	try:
		if not os.path.exists(MINHASHFOLDER):
			os.makedirs(MINHASHFOLDER)
		call_c()
	except:
		shared.error("2", ["min_hash", ""])
		return -1
	try:
		shared.insert_to_db("min_hash", "", "Finished")
	except:
		shared.error("10", ["min_hash", ""])
>>>>>>> 15d648cbfdb5aec698ff3667d6e94a5147f5613a
		return -1
	return 1

"""
Save the k-shingles to a database to be accessed in the c program

params: shingles (created by shared.gen_shingles)
return:
"""
<<<<<<< HEAD
def insert_shingles(shingles, documents):
	conn = sqlite3.connect(SHINGLEDB)
	c = conn.cursor()
=======
# TODO: keep this db? (right now it's kept)
def insert_shingles(shingles, documents):
	conn = sqlite3.connect(SHINGLEDB)
	c = conn.cursor()
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name="\
		"'Shingle'")
>>>>>>> 15d648cbfdb5aec698ff3667d6e94a5147f5613a
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

<<<<<<< HEAD
=======
"""
Call the c file to do the expensive functions for hashing

params:
return:
"""
def call_c():
	temp = os.path.abspath(__file__)
	temp = os.path.realpath(temp)
	temp = os.path.dirname(temp)
	path = os.path.join(temp, "minHash.so")
	testlib = ctypes.CDLL(path)
	testlib.callMinHash()
	return 1

>>>>>>> 15d648cbfdb5aec698ff3667d6e94a5147f5613a
min_hash()