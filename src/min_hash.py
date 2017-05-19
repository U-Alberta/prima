#!/usr/bin/python
import ctypes
import datetime
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
import sqlite3
import sys

PUNC = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, "*":0, \
	"(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0, 	"}":0, \
	"|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, ">":0, "/":0, "?":0}
"""
Should we let the user specify this? I think we could have 3 as a default and 
if the user wants to change it they can in the arguments.
"""
SHINGLES = 3
SHINGLEDB = "processed/shingles.db"
HISTDB = "processed/hist.db"
MINHASHFOLDER = "processed/min_hash"

def min_hash():
	if len(sys.argv) != 1:
		print("Invalid number of command line arguments")
		print("Usage: ~/min_hash.sh")
		return -1
	try:
		shingles = get_shingles()
	except:
		print("Error generating {}-shingles".format(SHINGLES))
		return -1
	try:
		insert_shingles(shingles)
	except:
		print("Error saving shingles to database {}".format(SHINGLEDB))
		return -1
	try:
		call_c()
	except:
		print("Error calling c functions for hashing")
		return -1
	try:
		insert_to_db()
	except:
		print("Error saving to history database {}".format(HISTDB))
		return -1
	return 1

"""
Parse through all the documents in the corpus getting k-shingles.
"""
def get_shingles():
	s = []
	docid = -1
	for item in sorted(os.listdir("source")):
		itemid = "".join(item.split("_"))
		for file in sorted(os.listdir("source/"+item)):
			fileid = file.split(".")[0]
			docname = "source/"+itemid+"/"+fileid
			try:
				doc = open("source/"+item+"/"+file, "r")
				docid+=1
				shingle = []
				for i in range(0, SHINGLES):
					shingle.append("")
				for line in doc:
					sentence_list = sent_tokenize(line.decode("utf-8"))
					for sentence in sentence_list:
						for term in word_tokenize(sentence):
							if term[0] not in PUNC.keys():
								try:
									term = term.lower()
									for i in range(0, SHINGLES):
										if shingle[i] == "":
											shingle[i] = term
											break
									if shingle[-1] != "":
										shingle_str = " ".join(shingle)
										s.append((docid, docname, shingle_str))
										for i in range(0, SHINGLES-1):
											shingle[i] = shingle[i+1]
										shingle[-1] = ""
								except:
									print("Error with term {}".format(term))
			except:
				print("Error opening document {}".format(docname))
	return s

"""
Save the k-shingles to a database to be accessed in the c program
"""
# TODO: keep this db? (right now it's kept)
def insert_shingles(shingles):
	conn = sqlite3.connect(SHINGLEDB)
	c = conn.cursor()
	c.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='Shingle'")
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

"""
Insert the command used, output, and time run to the history database.
"""
def insert_to_db():
	time = datetime.datetime.now()
	line = ("min_hash", "", True, time,)
	conn = sqlite3.connect(HISTDB)
	c = conn.cursor()
	c.execute("INSERT INTO History VALUES(?,?,?,?)", line)
	conn.commit()
	conn.close()
	return 1

min_hash()