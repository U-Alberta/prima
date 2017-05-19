#!/usr/bin/python
import datetime
from gensim import corpora, models
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
import sqlite3
import sys

PUNC = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, "*":0, \
	"(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0, 	"}":0, \
	"|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, ">":0, "/":0, "?":0}
TFIDFFOLDER = "processed/tfidf"
HISTDB = "processed/hist.db"
IIDB = "processed/inverted_index.db"

# TODO: allow to work on specific directories like word_count?
def tfidf():
	if len(sys.argv) != 1:
		print("Invalid number of command line arguments")
		print("Usage: ~/tfidf.sh")
		return -1
	try:
		texts, documents = build_texts()
	except:
		print("Error parsing through documents in collection")
		return -1
	try:
		tfidf, raw_tf, dictionary = get_tfidf(texts)
	except:
		print("Error calculating tfidf values")
		return -1
	try:
		tokens, postings = write_to_files(tfidf, raw_tf, dictionary, documents)
	except:
		print("Error saving result to files")
		return -1
	try:
		insert_inverted_index(tokens, postings)
	except:
		print("Error saving to inverted index database {}".format(IIDB))
		return -1
	try:
		insert_to_db()
	except:
		print("Error saving to history database {}".format(HISTDB))
		return -1
	return 1

"""
Parse through all the documents in the corpus, generating a list of words and 
documents.
"""
def build_texts():
	texts = []
	documents = []
	raw_df = {}
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
									if term not in raw_df.keys():
										raw_df[term] = 0
									raw_df[term]+=1
								except:
									pass
				texts.append(doc_text)
			except:
				print("Error opening document {}".format(docid))
	return texts, documents

"""
Use the gensim library to calculate tfidf.
"""
def get_tfidf(texts):
	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]
	tfidf = models.TfidfModel(corpus)
	corpus_tfidf = tfidf[corpus]
	return corpus_tfidf, corpus, dictionary

"""
Write the tf, df, and tf-idf values of terms and documents to three files in 
the processed/tfidf folder.
"""
def write_to_files(tfidf, raw_tf, dictionary, documents):
	tokens = []
	postings = []
	raw_df = {}
	if not os.path.exists(TFIDFFOLDER):
		os.makedirs(TFIDFFOLDER)
	idf_file = open(TFIDFFOLDER+"/tfidf.txt", "w")
	idf_file.write("term, document:\ttf-idf\n\n")
	tf_file = open(TFIDFFOLDER+"/tf.txt", "w")
	tf_file.write("term, document:\ttf\n\n")
	df_file = open(TFIDFFOLDER+"/df.txt", "w")
	df_file.write("term:\tdf\n\n")
	i = 0
	for doc_tfidf in tfidf:
		doc_tf = raw_tf[i]
		docid = documents[i]
		j = 0
		for posting in doc_tfidf:
			token_id = posting[0]
			term = dictionary[token_id]
			tfidf = posting[1]
			tf = doc_tf[j][1]
			line = term+", "+docid+":\t"+str(tfidf)+"\n"
			idf_file.write(line)
			line = term+", "+docid+":\t"+str(tf)+"\n"
			tf_file.write(line)
			postings.append((token_id, i, tf, tfidf))
			if term not in raw_df.keys():
				raw_df[term] = (0, token_id)
			tmp = raw_df[term][0]
			raw_df[term] = (tmp+1, token_id)
			j+=1
		i+=1
	for term in raw_df.keys():
		df = raw_df[term][0]
		token_id = raw_df[term][1]
		tokens.append((term, df, token_id))
		line = term+":\t"+str(df)+"\n"
		df_file.write(line)
	idf_file.close()
	tf_file.close()
	df_file.close()
	return tokens, postings

"""
This inserts all rows of the inverted index to a SQLite database.
"""
def insert_inverted_index(tokens, postings):
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

"""
Insert the command used, output, and time run to the history database.
"""
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