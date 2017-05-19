#!/usr/bin/python
import datetime
import numpy as np
from scipy import linalg as la
import os
import pandas as pd
import sqlite3
import sys

PUNC = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, "*":0, \
	"(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0, 	"}":0, \
	"|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, ">":0, "/":0, "?":0}
LSIFOLDER = "processed/lsi/"
HISTDB = "processed/hist.db"

# TODO: queries?
# TODO: allow to work on specific directories like word_count?
# TODO: gensim
def lsi():
	if len(sys.argv) != 2:
		print("Invalid number of command line arguments")
		print("Usage: ~/lsi.sh k")
		return -1
	k = int(sys.argv[1])
	try:
		tokens, docs = get_toks_docs()
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
	try:
		write_to_file(ck, docs)
	except:
		print("Error saving result to file")
		return -1
	try:
		insert_to_db(k)
	except:
		print("Error saving to history database")
		return -1
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
						if term[0] not in PUNC.keys():
							try:
								term = term.lower()
								if term not in toks:
									toks.append(term)
							except:
								pass
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
						if term[0] not in PUNC.keys():
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

# Using the linear algebra python library, calculate the svd, adjust it to 
# the dimensions of k, and produce a new matrix ck as output.
def get_ck(ct, k):
	c = ct.T
	u_prime, s, vt = la.svd(c)
	m, n = c.shape
	sigma_prime = la.diagsvd(s, min(m, n), min(m, n))
	sigma, u = get_k_sigma_u(sigma_prime, u_prime, k)
	#print("u:")
	#for _ in u: print _
	#print("sigma:")
	#for _ in sigma: print _
	ck = u*sigma
	ck = np.matrix(ck)
	#print("u*sigma:")
	#for _ in ck: print _
	vt = vt[:k]
	vt = np.matrix(vt)
	#print ("vt:")
	#for _ in vt: print _
	#two = sigma*vt
	#two = np.matrix(two)
	#print("sigma*vt:")
	#for _ in two: print _
	ck = ck*vt
	ck = np.matrix(ck)
	#print("ck:")
	#for _ in ck: print _
	return ck

# Reduce the dimensions of sigma to kxk and of u to kxm.
def get_k_sigma_u(sigma, u, k):
	new_sigma = []
	new_u = []
	for i in range(0, len(u)):
		new_u.append(u[i][:k])
		if i < k:
			new_sigma.append(sigma[i][:k])
	return np.matrix(new_sigma), np.matrix(new_u)

# Write the newly created matrix ck to a csv file in the processed/lsi folder.
def write_to_file(ck, docs):
	df = pd.DataFrame(ck, columns=docs)
	if not os.path.exists(LSIFOLDER):
		os.makedirs(LSIFOLDER)
	df.to_csv(LSIFOLDER+"lsi.csv")
	return 1

# Insert the command used, output, and time run to the history database.
def insert_to_db(k):
	time = datetime.datetime.now()
	line = ("lsi", k, "True", time,)
	conn = sqlite3.connect(HISTDB)
	c = conn.cursor()
	c.execute("INSERT INTO History VALUES(?,?,?,?)", line)
	conn.commit()
	conn.close()
	return 1

lsi()