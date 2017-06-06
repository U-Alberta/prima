#!/usr/bin/python
import json
import os
import shared
import sqlite3
import sys

IIDB = "processed/inverted_index.db"
TFIDFFOLDER = "processed/tfidf/"

# TODO: allow to work on specific directories like word_count?
def tfidf():
	if len(sys.argv) not in [1, 2]:
		shared.error("11", ["tfidf", ""])
		return -1
	filetype = sys.argv[1]
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
		tokens, postings = write_to_files(tfidf, raw_tf, dictionary, documents, filetype)
	except:
		shared.error("8", ["tfidf", ""])
		return -1
	"""
	I don't need an inverted_index anymore for my other functions so should this
	be created?
	"""
	"""
	try:
		insert_inverted_index(tokens, postings)
	except:
		shared.error("9", ["tfidf", ""], IIDB)
		return -1
	"""
	try:
		shared.insert_to_db("tfidf", "", "Finished")
	except:
		shared.error("10", ["tfidf", ""])
		return -1
	return 1

"""
Write the tf, df, and tf-idf values of terms and documents to three files in 
the processed/tfidf folder.
"""
def write_to_files(tfidf, raw_tf, dictionary, documents, filetype):
	data = {"df":{}}
	tokens = []
	postings = []
	raw_df = {}
	if filetype == ".tsv": separator = "\t"
	else: separator =", "
	if not os.path.exists(TFIDFFOLDER):
		os.makedirs(TFIDFFOLDER)
	idf_file = open(TFIDFFOLDER+"tfidf"+filetype, "w")
	idf_file.write("term{}document{}tf-idf\n".format(separator, separator))
	tf_file = open(TFIDFFOLDER+"tf"+filetype, "w")
	tf_file.write("term{}document{}tf\n".format(separator, separator))
	df_file = open(TFIDFFOLDER+"df"+filetype, "w")
	df_file.write("term{}df\n".format(separator))
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
			line = term+separator+docid+separator+str(tfidf)+"\n"
			idf_file.write(line)
			data[docid]["tf-idf"][term] = tfidf
			line = term+separator+docid+separator+str(tf)+"\n"
			tf_file.write(line)
			data[docid]["tf"][term] = tf
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
		line = term+separator+str(df)+"\n"
		df_file.write(line)
		data["df"][term] = df
	idf_file.close()
	tf_file.close()
	df_file.close()
	with open(TFIDFFOLDER+"data.json", "w") as outfile:
		json.dump(data, outfile, sort_keys=True, indent=4)
	return tokens, postings

"""
This inserts all rows of the inverted index to a SQLite database.
May be deleted.
"""
def insert_inverted_index(tokens, postings):
	conn = sqlite3.connect(IIDB)
	c = conn.cursor()
	c.execute("CREATE TABLE Token(token text, df int, token_id int PRIMARY KEY)")
	c.execute("CREATE TABLE Posting(token_id int, doc_id int, tf int, tf_idf "\
		"float, FOREIGN KEY(token_id) REFERENCES Token(token_id))")
	conn.commit()
	c.executemany("INSERT INTO Token VALUES (?,?,?)", tokens)
	c.executemany("INSERT INTO Posting VALUES (?,?,?,?)", postings)
	conn.commit()
	conn.close()
	return 1

tfidf()