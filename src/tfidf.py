#!/usr/bin/python
import datetime
import linecache
import math
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
import sqlite3
import sys

TFIDFFOLDER = "processed/tfidf"
TFFILE = "processed/tfidf/tf.txt"
DFFILE = "processed/tfidf/df.txt"
IDFFILE = "processed/tfidf/idf.txt"
DBFOLDER = "processed/hist.db"

def tfidf():
	if len(sys.argv) != 1:
		print("Invalid number of command line arguments")
		return -1
	try:
		tf, df, tokens, n = get_tf_df()
	except:
		print("Error getting term and document frequency")
		return -1
	try:
		idf = calc_idf(n, df)
	except:
		print("Error calculating idf")
		return -1
	try:
		write_to_files(tokens, tf, df, idf)
	except:
		print("Error writing values to files")
		return -1
	try:
		insert_to_db()
	except:
		print("Error saving to history database")
		return -1
	return 1

# Iterate through all the documents in the collection counting occurances of 
# terms both in the corpus and in individual documents. Save all the tokens 
# to the list tokens and sort it alphabetically to use later (note: this is 
# slow but it makes for prettier output in the documents).
def get_tf_df():
	tf = {}
	df = {}
	tokens = []
	n = 0
	punc = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, \
		"*":0, "(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0, \
		"}":0, "\\":0, "|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, \
		">":0, "/":0, "?":0, "'d":0, "'ll":0, "'re":0, "'s":0, "'ve":0}
	for item in os.listdir("source"):
		for file in os.listdir("source/"+item):
			docid = file.split(".")[0]
			try:
				doc = open("source/"+item+"/"+file)
				n+=1
				for line in doc:
					sentence_list = sent_tokenize(line)
					for sentence in sentence_list:
						for term in word_tokenize(sentence):
							if term[0] not in punc:
								try:
									term = term.lower()
								except:
									pass
								if term not in tf.keys():
									tokens.append(term)
									tf[term] = 0
									df[term] = {}
								if docid not in df[term].keys():
									clean_item = "".join(item.split("_"))
									df[term][clean_item+"_"+docid] = 0
								df[term][clean_item+"_"+docid]+=1
								tf[term]+=1
			except:
				print("Problem reading document {}/{}, moving on".format(item, file))
				pass
			doc.close()
	tokens.sort()
	return tf, df, tokens, n

# Use the df values to calculate idf for all tokens in each document.
def calc_idf(n, df):
	corpus_idf = {}
	for t in df.keys():
		for d in df[t].keys():
			frequency_t_d = df[t][d]
			idf = math.log10(float(n)/frequency_t_d)
			if t not in corpus_idf.keys():
				corpus_idf[t] = {}
			corpus_idf[t][d] = idf
	return corpus_idf

# Write the tf, df, and idf values of terms and documents to three files in the 
# processed/tfidf folder.
def write_to_files(tokens, tf, df, idf):
	insert_errors = 0
	if not os.path.exists(TFIDFFOLDER):
		os.makedirs(TFIDFFOLDER)
	tf_file = open(TFFILE, "w")
	tf_file.write("term\tfrequency")
	df_file = open(DFFILE, "w")
	df_file.write("term, document:\tfrequency")
	idf_file = open(IDFFILE, "w")
	df_file.write("term, document:\tinverse document frequency")
	for t in tokens:
		value = str(tf[t])
		tf_file.write(t+":\t"+value)
		tf_file.write("\n")
		for doc in df[t].keys():
			value = str(df[t][doc])
			df_file.write(t+", "+doc+":\t"+value)
			df_file.write("\n")
			value = str(idf[t][doc])
			idf_file.write(t+", "+doc+":\t"+value)
			idf_file.write("\n")
	tf_file.close()
	df_file.close()
	idf_file.close()
	return 1

# Insert the command used, output, and time run to the history database.
def insert_to_db():
	time = datetime.datetime.now()
	line = ("tfidf", "", "True", time,)
	conn = sqlite3.connect(DBFOLDER)
	c = conn.cursor()
	c.execute("INSERT INTO History VALUES(?,?,?,?)", line)
	conn.commit()
	conn.close()
	return 1

tfidf()