#!/usr/bin/python
import json
import os
import shared
import sqlite3
import sys

IIDB = "processed/inverted_index.db"
TFIDFFOLDER = "processed/tfidf/"

def tfidf():
	if len(sys.argv) != 1:
		shared.error("11", ["tfidf", ""])
		return -1
	try:
		texts, documents = shared.build_texts("tfidf")
	except:
		shared.error("0", ["tfidf", ""])
		return -1
	try:
		tfidf, raw_tf, dictionary = shared.get_tfidf(texts)
	except:
		shared.error("1", ["tfidf", ""])
		return -1
	try:
		tokens, postings = write_to_files(tfidf, raw_tf, dictionary, documents)
	except:
		shared.error("8", ["tfidf", ""])
		return -1
	try:
		shared.insert_to_db("tfidf", "", "Finished")
	except:
		shared.error("10", ["tfidf", ""])
		return -1
	return 1

"""
Write the tf, df, and tf-idf values of terms and documents to three files in 
the processed/tfidf folder.

params: tfidf (the tfidf values of all terms in all documents), raw_tf (term 
	frequencies), dictionary (a list of all terms in the corpus), documents (a 
	list of all documents in the corpus)
return: tokens (list of tuples to be inserted to inverted_index), postings 
	(list of tuples to be inserted to inverted_index) <<<<<<<<<<<<<<<<<<<<<<change that??
"""
def write_to_files(tfidf, raw_tf, dictionary, documents):
	data = {"df":{}}
	tokens = []
	postings = []
	raw_df = {}
	comma = ", "
	if not os.path.exists(TFIDFFOLDER):
		os.makedirs(TFIDFFOLDER)
	idf_file = open(TFIDFFOLDER+"tfidf.csv", "w")
	idf_file.write("term{}document{}tf-idf\n".format(comma, comma))
	tf_file = open(TFIDFFOLDER+"tf.csv", "w")
	tf_file.write("term{}document{}tf\n".format(comma, comma))
	df_file = open(TFIDFFOLDER+"df.csv", "w")
	df_file.write("term{}df\n".format(comma))
	i = 0
	for doc_tfidf in tfidf:
		doc_tf = raw_tf[i]
		docid = documents[i]
		data[docid] = {"tf-idf":{}, "tf":{}}
		j = 0
		for posting in doc_tfidf:
			token_id = posting[0]
			term = dictionary[token_id]
			tfidf = posting[1]
			tf = doc_tf[j][1]
			line = term+comma+docid+comma+str(tfidf)+"\n"
			idf_file.write(line)
			data[docid]["tf-idf"][term] = tfidf
			line = term+comma+docid+comma+str(tf)+"\n"
			tf_file.write(line)
			data[docid]["tf"][term] = tf
			postings.append((token_id, i, tf, tfidf))
			if term not in raw_df.keys():
				raw_df[term] = (0, token_id)
			tmp = raw_df[term][0]
			raw_df[term] = (tmp+1, token_id)
			j+=1
		if data[docid] == {"tf-idf":{}, "tf":{}}:
			del data[docid]
		i+=1
	for term in raw_df.keys():
		df = raw_df[term][0]
		token_id = raw_df[term][1]
		tokens.append((term, df, token_id))
		line = term+comma+str(df)+"\n"
		df_file.write(line)
		data["df"][term] = df
	idf_file.close()
	tf_file.close()
	df_file.close()
	with open(TFIDFFOLDER+"data.json", "w") as outfile:
		json.dump(data, outfile, sort_keys=True, indent=2)
	return tokens, postings

tfidf()