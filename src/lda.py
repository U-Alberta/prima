#!/usr/bin/python
import datetime
from gensim import corpora, models
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
import pandas as pd
import sqlite3
import sys

PUNC = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, "*":0, \
	"(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0, 	"}":0, \
	"|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, ">":0, "/":0, "?":0}
LDAFOLDER = "processed/lda/"
HISTDB = "processed/hist.db"

# TODO: allow to work on specific directories like word_count?
def lda():
	if len(sys.argv) != 2:
		print("Invalid number of command line arguments")
		print("Usage: ~/lda.sh k")
		return -1
	k = int(sys.argv[1])
	try:
		texts, documents = build_texts()
	except:
		print("Error getting tokens")
		return -1
	try:
		ck = get_lda(texts, k)
	except:
		print("Error getting df matrix")
		return -1
	try:
		write_to_file(ck, documents)
	except:
		print("Error saving result to file")
		return -1
	try:
		insert_to_db(k)
	except:
		print("Error saving to history database")
		return -1
	return 1

"""
Parse through all the documents in the corpus, generating a list of words and 
documents.
"""
def build_texts():
	texts = []
	documents = []
	for item in sorted(os.listdir("source")):
		itemid = "".join(item.split("_"))
		for file in sorted(os.listdir("source/"+item)):
			fileid = file.split(".")[0]
			docid = "source/"+itemid+"/"+fileid
			try:
				doc = open("source/"+item+"/"+file, "r")
				documents.append(docid)
				doc_text = []
				for line in doc:
					sentence_list = sent_tokenize(line.decode("utf-8"))
					for sentence in sentence_list:
						for term in word_tokenize(sentence):
							if term[0] not in PUNC.keys():
								try:
									term = term.lower()
									doc_text.append(term)
								except:
									pass
				texts.append(doc_text)
			except:
				print("Error opening document {}".format(docid))
	return texts, documents

"""
I think line 85 trains the model on corpus and then loads the same model into 
lda which isn't great. TODO: figure out what's going on.
"""
def get_lda(texts, k):
	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]
	tfidf = models.TfidfModel(corpus)
	lda = models.LdaModel(corpus, id2word=dictionary, num_topics=k)
	corpus_lda = lda[corpus]
	ck = []
	for i in range(0, len(corpus_lda[0])):
		ck.append([])
	for row in corpus_lda:
		for i in range(0, len(row)):
			ck[i].append(row[i][1])
	return ck

"""
Write the newly created matrix ck to a csv file in the processed/lda folder.
"""
def write_to_file(ck, docs):
	df = pd.DataFrame(ck, columns=docs)
	if not os.path.exists(LDAFOLDER):
		os.makedirs(LDAFOLDER)
	df.to_csv(LDAFOLDER+"lda.csv")
	return 1

"""
Insert the command used, output, and time run to the history database.
"""
def insert_to_db(k):
	time = datetime.datetime.now()
	line = ("lda", k, "True", time,)
	conn = sqlite3.connect(HISTDB)
	c = conn.cursor()
	c.execute("INSERT INTO History VALUES(?,?,?,?)", line)
	conn.commit()
	conn.close()
	return 1

lda()