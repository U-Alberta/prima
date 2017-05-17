#!/usr/bin/python
import datetime
import linecache
import math
from minHash import *
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import numpy as np
from scipy import linalg as la
import os
import pandas as pd
import sqlite3
import sys

PUNC = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, "*":0, \
	"(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0, 	"}":0, \
	"\\":0, "|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, ">":0, \
	"/":0, "?":0}
SHINGLES = 3 # Should we let the user specify this?
HISTDB = "processed/hist.db"
MINHASHFOLDER = "processed/min_hash"

#
def min_hash():
	if len(sys.argv) != 1:
		print("Invalid number of command line arguments")
		print("Usage: ~/min_hash.sh")
		return -1
	# Shingle in python
	try:
		shingles, N = get_shingles()
	except:
		print("Error generating {}-shingles".format(SHINGLES))
	# Do all the hashes in c
	print "Result from getHash:", getHash()

def get_shingles():
	s = {}
	n = 0
	for item in sorted(os.listdir("source")):
		itemid = "".join(item.split("_"))
		for file in sorted(os.listdir("source/"+item)):
			fileid = file.split(".")[0]
			docid = "source/"+itemid+"/"+fileid
			try:
				doc = open("source/"+item+"/"+file, "r")
				n+=1
				s[docid] = {"length":0, "shingles":[]}
				shingle = []
				for i in range(0, SHINGLES):
					shingle.append("")
				for line in doc:
					sentence_list = sent_tokenize(line.decode("utf-8"))
					for sentence in sentence_list:
						for term in word_tokenize(sentence):
							if term not in PUNC:
								try:
									term = term.lower()
									for i in range(0, SHINGLES):
										if shingle[i] == "":
											shingle[i] = term
											break
									if shingle[-1] != "":
										s[docid]["shingles"].append(" ".join(shingle))
										s[docid]["length"]+=1 #changed this, check it works
										for i in range(0, SHINGLES-1):
											shingle[i] = shingle[i+1]
										shingle[-1] = ""
								except:
									print("Error with term {}".format(term))
			except:
				print("Error opening document {}".format(docid))
	return s, n

# Write the word count value to the generated outfilename in the 
# processed/word_count folder.
# TODO: change this
def write_to_file(output):
	if not os.path.exists(MINHASHFOLDER):
		os.makedirs(MINHASHFOLDER, "w")
	outfile = open(MINHASHFOLDER+"minhash.txt", "w")
	outfile.write(output)
	outfile.close()

# Insert the command used, output, and time run to the history database.
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