#!/usr/bin/python
import datetime
import linecache
import math
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import numpy as np
from scipy import linalg as la
import os
import pandas as pd
import sqlite3
import sys

INFINITY = 1000000000
DBFOLDER = "processed/hist.db"
LSIFOLDER = "processed/lsi/"
DBFOLDER = "processed/hist.db"
ROUND = 5
PUNC = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, \
	"*":0, "(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0, \
	"}":0, "\\":0, "|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, \
	">":0, "/":0, "?":0}

def lsi():
	if len(sys.argv) != 2:
		print("Invalid number of command line arguments")
		return -1
	k = int(sys.argv[1])
	try:
		tokens, docs = get_toks_docs()
		tokens = ['ship','boat','ocean','voyage','trip']
	except:
		print("Error getting tokens")
		return -1
	try:
		ct = get_ct(tokens)
	except:
		print("Error getting df matrix")
		return -1
	try:
		ck = get_ck(ct, k)
	except:
		print("Error getting c{} matrix".format(k))
		return -1
	"""	
	try:
		write_to_file(ck, tokens, docs)
	except:
		print("Error writing to file")
		return -1
	try:
		insert_to_db()
	except:
		print("Error writing to database")
		return -1
	"""
	return 1

# Iterate through all the documents in the collection saving all the tokens in 
# the collection to a sorted list to be used later creating a matrix.
def get_toks_docs():
	toks = []
	docs = []
	for item in os.listdir("source"):
		for file in sorted(os.listdir("source/"+item)):
			docname = "source/"+item+"/"+file
			doc = open(docname)
			docs.append(docname)
			for line in doc:
				sentence_list = sent_tokenize(line)
				for sentence in sentence_list:
					for term in word_tokenize(sentence):
						if term[0] not in PUNC:
							try:
								term = term.lower()
							except:
								pass
							if term not in toks:
								toks.append(term)
			doc.close()
	toks.sort()
	return toks, docs

# Iterate through all the documents in the collection counting occurances of 
# terms in each document and appending them to the appropriate position of the 
# df dictionary.
def get_ct(tokens):
	ct = []
	i = 0
	for item in os.listdir("source"):
		for file in sorted(os.listdir("source/"+item)):
			docname = "source/"+item+"/"+file
			doc = open(docname)
			row = [0]*len(tokens)
			for line in doc:
				sentence_list = sent_tokenize(line)
				for sentence in sentence_list:
					for term in word_tokenize(sentence):
						if term[0] not in PUNC:
							try:
								term = term.lower()
								loc = tokens.index(term)
								row[loc]+=1
							except:
								pass
			i+=1
			ct.append(row)
			doc.close()
	return np.matrix(ct)

#
def get_ck(ct, k):
	c = ct.T
	u, s, vt = la.svd(c)
	m, n = c.shape
	width = min(m, n)
	max_dim = max(m, n)
	sigma = la.diagsvd(s, m, n)
	sigma = get_k_sigma(sigma, k, width)
	vt = vt[:width]
	ck = np.multiply(u, sigma)
	for row in ck: print row
	ck = np.asmatrix(ck)
	vt = np.asmatrix(vt)
	ck = ck*vt
	return ck

#
def get_k_sigma(sigma, k, width):
	new_sigma = []
	empty_row = []
	for _ in range(0, width):
		empty_row.append(float(0))
	for row in sigma:
		if k > 0:
			new_sigma.append(row[:width])
		else:
			new_sigma.append(empty_row)
		k-=1
	return new_sigma

# Write the matrix of term and document frequency to a csv file in the 
# processed/lsi folder.
def write_to_file(ck, tokens, docs):
	df = pd.DataFrame(ck, index=tokens, columns=docs)
	if not os.path.exists(LSIFOLDER):
		os.makedirs(LSIFOLDER)
	df.to_csv(LSIFOLDER+"lsi.csv")
	return 1

# Insert the command used, output, and time run to the history database.
def insert_to_db():
	time = datetime.datetime.now()
	line = ("lsi", "", "True", time,)
	conn = sqlite3.connect(DBFOLDER)
	c = conn.cursor()
	c.execute("INSERT INTO History VALUES(?,?,?,?)", line)
	conn.commit()
	conn.close()
	return 1

lsi()