#!/usr/bin/python
import datetime
import linecache
import math
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
import pandas as pd
import sqlite3
import sys

DBFOLDER = "processed/hist.db"
LSIFOLDER = "processed/lsi/"
DBFOLDER = "processed/hist.db"

def lsi():
	if len(sys.argv) != 1:
		print("Invalid number of command line arguments")
		return -1
	try:
		tokens = get_toks_docs()
	except:
		print("Error getting tokens")
		return -1
	try:
		df = get_df(tokens)
	except:
		print("Error getting df matrix")
		return -1
	try:
		df = pd.DataFrame(df, index=tokens)
	except:
		print("Error building Pandas DataFrame")
		return -1
	try:
		write_to_file(df)
	except:
		print("Error writing to file")
		return -1
	try:
		insert_to_db()
	except:
		print("Error writing to database")
	return 1

# Iterate through all the documents in the collection saving all the tokens in 
# the collection to a sorted list to be used later creating a matrix.
def get_toks_docs():
	punc = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, \
		"*":0, "(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0, \
		"}":0, "\\":0, "|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, \
		">":0, "/":0, "?":0}
	toks = []
	for item in os.listdir("source"):
		for file in os.listdir("source/"+item):
			docname = "source/"+item+"/"+file
			doc = open(docname)
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
	return toks

# Iterate through all the documents in the collection counting occurances of 
# terms in each document and appending them to the appropriate position of the 
# df dictionary.
def get_df(tokens):
	df = {}
	punc = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, \
		"*":0, "(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0, \
		"}":0, "\\":0, "|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, \
		">":0, "/":0, "?":0}
	for item in os.listdir("source"):
		for file in os.listdir("source/"+item):
			docname = "source/"+item+"/"+file
			doc = open(docname)
			df[docname] = [0]*len(tokens)
			for line in doc:
				sentence_list = sent_tokenize(line)
				for sentence in sentence_list:
					for term in word_tokenize(sentence):
						if term[0] not in punc:
							try:
								term = term.lower()
								loc = tokens.index(term)
								df[docname][loc]+=1
							except:
								pass
			doc.close()
	return df

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