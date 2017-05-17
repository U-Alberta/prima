#!/usr/bin/python
import datetime
import linecache
import math
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
import sqlite3
import sys

PUNC = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, "*":0, \
	"(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0, 	"}":0, \
	"\\":0, "|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, ">":0, \
	"/":0, "?":0, "'d":0, "'ll":0, "'re":0, "'s":0, "'ve":0}
TFIDFFOLDER = "processed/tfidf"
TFFILE = "processed/tfidf/tf.txt"
DFFILE = "processed/tfidf/df.txt"
IDFFILE = "processed/tfidf/tfidf.txt"
HISTDB = "processed/hist.db"
IIDB = "processed/inverted_index.db"

# TODO: allow to work on specific directories like word_count?
def tfidf():
	if len(sys.argv) != 1:
		print("Invalid number of command line arguments")
		print("Usage: ~/tfidf.sh")
		return -1
	try:
		corpus_list, n = build_corpus_list()
	except:
		print("Error building corpus list")
		return -1
	try:
		inverted_index = build_inverted_index(corpus_list)
	except:
		print("Error building inverted index")
		return -1
	try:
		tokens, postings = tf_idf_calc(inverted_index, n)
	except:
		print("Error calculating tfidf values")
		return -1
	try:
		write_to_files(inverted_index)
	except:
		print("Error saving result to files")
		return -1
	try:
		insert_inverted_index(inverted_index, tokens, postings)
	except:
		print("Error saving to inverted index database {}".format(IIDB))
		return -1
	try:
		insert_to_db()
	except:
		print("Error saving to history database {}".format(HISTDB))
		return -1
	return 1

# This builds a list of tuples which hold all the terms along with the documents 
# they appear in.
def build_corpus_list():
	n = 0
	corpus_list = []
	for item in sorted(os.listdir("source")):
		itemid = "".join(item.split("_"))
		for file in sorted(os.listdir("source/"+item)):
			fileid = file.split(".")[0]
			docid = "source/"+itemid+"/"+fileid
			try:
				doc = open("source/"+item+"/"+file, "r")
				n+=1
				for line in doc:
					sentence_list = sent_tokenize(line.decode("utf-8"))
					for sentence in sentence_list:
						for term in word_tokenize(sentence):
							if term not in PUNC:
								try:
									term = term.lower()
								except:
									pass
								corpus_list.append((term, docid))
			except:
				print("Error opening document: {}".format(docid))
	corpus_list.sort(key=lambda tup: tup[0])
	return corpus_list, n

# This takes the corpus list and condenses it into an inverted index.
def build_inverted_index(corpus_list):
	inverted_index = {}
	i = 0
	prev_token = ""
	prev_docid = ""
	while i < len(corpus_list):
		token = corpus_list[i][0]
		docid = str(corpus_list[i][1])
		if token == prev_token:
			if prev_docid == docid:
				inverted_index[token]["postings"][docid]["tf"]+=1
			else:
				prev_docid = docid
				inverted_index[token]["df"]+=1
				inverted_index[token]["postings"][docid] = {"tf":1, "tf-idf":0}
		else:
			prev_token = token
			prev_docid = docid
			inverted_index[token] = {"df":1, "postings":{docid:{"tf":1, "tf-idf":0}}}
		i+=1
	return inverted_index

# This calculates the tf-idf value for each term in the inverted index and 
# while doing this also builds two lists which are used to do the mass 
# insert to the db.
def tf_idf_calc(inverted_index, n):
	token_id = 0
	tokens = []
	postings = []
	for key in inverted_index:
		token = inverted_index[key]
		token_id += 1
		df = token["df"]
		idf = math.log10(float(n)/df)
		tokens.append((key, df, token_id))
		for doc in token["postings"]:
			tf = token["postings"][doc]["tf"]
			tf_idf = tf * idf
			token["postings"][doc]["tf-idf"] = tf_idf
			postings.append((token_id, doc, tf, tf_idf))
	return tokens, postings

# Write the tf, df, and tf-idf values of terms and documents to three files in 
# the processed/tfidf folder.
def write_to_files(inverted_index):
	if not os.path.exists(TFIDFFOLDER):
		os.makedirs(TFIDFFOLDER)
	df_file = open(DFFILE, "w")
	df_file.write("term:\tdocument frequency\n\n")
	tf_file = open(TFFILE, "w")
	tf_file.write("term, document:\tterm frequency\n\n")
	idf_file = open(IDFFILE, "w")
	idf_file.write("term, document:\ttf-idf\n\n")
	for t in inverted_index.keys():
		value = str(inverted_index[t]["df"])
		df_file.write(t+":\t"+value+"\n")
		for doc in inverted_index[t]["postings"].keys():
			doc_posting = inverted_index[t]["postings"][doc]
			value = str(doc_posting["tf"])
			tf_file.write(t+", "+doc+":\t"+value+"\n")
			value = str(doc_posting["tf-idf"])
			idf_file.write(t+", "+doc+":\t"+value+"\n")
	tf_file.close()
	df_file.close()
	idf_file.close()
	return 1

# This inserts all rows of the inverted index to a SQLite database.
def insert_inverted_index(inverted_index, tokens, postings):
	conn = sqlite3.connect(IIDB)
	c = conn.cursor()
	c.execute("CREATE TABLE Token(token text, df int, token_id int PRIMARY KEY)")
	c.execute("CREATE TABLE Posting(token_id int, doc_id int, tf int, tf_idf float, FOREIGN KEY(token_id) REFERENCES Token(token_id))")
	conn.commit()
	c.executemany("INSERT INTO Token VALUES (?,?,?)", tokens)
	c.executemany("INSERT INTO Posting VALUES (?,?,?,?)", postings)
	conn.commit()
	conn.close()
	return 1

# Insert the command used, output, and time run to the history database.
def insert_to_db():
	time = datetime.datetime.now()
	line = ("tfidf", "", "True", time,)
	conn = sqlite3.connect(HISTDB)
	c = conn.cursor()
	c.execute("INSERT INTO History VALUES(?,?,?,?)", line)
	conn.commit()
	conn.close()
	return 1

tfidf()