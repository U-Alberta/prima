#!/usr/bin/python
import datetime
import linecache
import math
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import numpy as np
from numpy import linalg as la
import os
import pandas as pd
import sqlite3
import sys

INFINITY = 1000000000
DBFOLDER = "processed/hist.db"
LSIFOLDER = "processed/lsi/"
DBFOLDER = "processed/hist.db"

def lsi():
	if len(sys.argv) != 1:
		print("Invalid number of command line arguments")
		return -1
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
		c = transpose(ct)
	except:
		print("Error transposing matrix ct")
		return -1
	try:
		ck, k_tokens = get_k_svd(c, ct, tokens)
	except:
		print("Error generating svd matrices")
		return -1
	#print(k_tokens)
	df = pd.DataFrame(ck, index=tokens, columns=docs)
	#print(df)
	try:
		write_to_file(df)
	except:
		print("Error writing to file")
		return -1
	try:
		insert_to_db()
	except:
		print("Error writing to database")
		return -1
	return 1

# Iterate through all the documents in the collection saving all the tokens in 
# the collection to a sorted list to be used later creating a matrix.
def get_toks_docs():
	punc = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, \
		"*":0, "(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0, \
		"}":0, "\\":0, "|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, \
		">":0, "/":0, "?":0}
	toks = []
	docs = []
	for item in os.listdir("source"):
		for file in os.listdir("source/"+item):
			docname = "source/"+item+"/"+file
			doc = open(docname)
			docs.append(docname)
			for line in doc:
				sentence_list = sent_tokenize(line)
				for sentence in sentence_list:
					for term in word_tokenize(sentence):
						if term[0] not in punc:
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
	punc = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, \
		"*":0, "(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0, \
		"}":0, "\\":0, "|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, \
		">":0, "/":0, "?":0}
	i = 0
	for item in os.listdir("source"):
		for file in os.listdir("source/"+item):
			docname = "source/"+item+"/"+file
			doc = open(docname)
			row = [0]*len(tokens)
			for line in doc:
				sentence_list = sent_tokenize(line)
				for sentence in sentence_list:
					for term in word_tokenize(sentence):
						if term[0] not in punc:
							try:
								term = term.lower()
								loc = tokens.index(term)
								row[loc]+=1
							except:
								pass
			i+=1
			ct.append(row)
			doc.close()
	return ct

# Here k=2
# TODO: find a way to set a global value for k and use that
def get_k_svd(c, ct, tokens):
	u_prime = np.matmul(c, ct)
	eigen_u = la.eig(u_prime)
	u_values = eigen_u[0]
	u_double_prime = eigen_u[1]
	sigma_prime = []
	i = 0
	for eigenvalue in u_values:
		row = [0]*len(u_values)
		eigenvalue = round(eigenvalue, 5)
		sing_val = math.sqrt(eigenvalue)
		row[i] = sing_val
		sigma_prime.append(row)
		i+=1
	u, sigma, tokens = max_rows(u_double_prime, sigma_prime, tokens)
	v_prime = np.matmul(ct, c)
	eigen_v = la.eig(v_prime)
	v = -eigen_v[1]
	vt = transpose(v)
	ck = np.matmul(u, sigma)
	ck = np.matmul(ck, vt)
	return ck, tokens

def transpose(matrix):
	matrix_t = []
	for i in range(0,len(matrix[0])):
		column = []
		for j in range(0,len(matrix)):
			column.append(matrix[j][i])
		matrix_t.append(column)
	return matrix_t

def max_rows(u_double_prime, sigma_prime, tokens):
	new_tokens = []
	max1 = (-INFINITY, -1)
	max2 = (-INFINITY, -1)
	for i in range(0, len(sigma_prime)):
		row = sigma_prime[i]
		if sum(row) > max1[0]:
			max2 = max1
			max1 = (sum(row), i)
		elif sum(row) > max2[0]:
			max2 = (sum(row), i)
	max_indices = [max1[1], max2[1]]
	u = []
	sigma = []
	for _ in range(0, len(sigma_prime)):
		max1 = min(max_indices)
		u1_val = round(u_double_prime[_][max1], 5)
		max2 = max(max_indices)
		u2_val = round(u_double_prime[_][max2], 5)
		u.append([u1_val, u2_val])
		if _ in max_indices:
			new_tokens.append(tokens[_])
			sigma1_val = round(sigma_prime[_][max1], 5)
			sigma2_val = round(sigma_prime[_][max2], 5)
			sigma.append([sigma1_val, sigma2_val])
	return u, sigma, new_tokens

# Write the matrix of term and document frequency to a csv file in the 
# processed/lsi folder.
def write_to_file(df):
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