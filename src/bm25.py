#!/usr/bin/python
import datetime
from gensim import corpora, summarization
import os
import shared
import sys
import time

BM25FOLDER = "processed/bm25/"

def bm_25():
<<<<<<< HEAD
	args = sys.argv[0:]
	if len(args) == 2:
		k = 10
		q = args[1].split(" ")
	elif len(args) == 3:
		k = int(args[1])
		q = args[2].split(" ")
	else:
		shared.error("11", ["bm25", ""])
		return -1
=======
	if len(sys.argv) < 2:
		shared.error("11", ["bm25", ""])
		return -1
	q = sys.argv[1:]
>>>>>>> 15d648cbfdb5aec698ff3667d6e94a5147f5613a
	try:
		texts, documents = shared.build_texts("bm25")
	except:
		shared.error("0", ["bm25", " ".join(q)])
		return -1
	try:
		scores = score(texts, q)
	except:
		shared.error("1", ["bm25", " ".join(q)])
		return -1
	try:
<<<<<<< HEAD
		write_to_file(scores, documents, q, k)
=======
		write_to_file(scores, documents, q)
>>>>>>> 15d648cbfdb5aec698ff3667d6e94a5147f5613a
	except:
		shared.error("8", ["bm25", " ".join(q)])
	try:
		shared.insert_to_db("bm25", "", "Finished")
	except:
		shared.error("10", ["bm25", " ".join(q)])
		return -1
	return 1

<<<<<<< HEAD
=======

>>>>>>> 15d648cbfdb5aec698ff3667d6e94a5147f5613a
"""
Use the gensim library to score the query using the BM25 model.
https://stackoverflow.com/questions/40966014/how-to-use-gensim-bm25-ranking-in-python

params: texts (created by shared.build_texts), q (space-separated query)
return: 
"""
def score(texts, q):
	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]
	query_dict = dictionary.doc2bow(q)
	bm25_model = summarization.bm25.BM25(corpus)
	average_idf = sum(map(lambda k: float(bm25_model.idf[k]), \
		bm25_model.idf.keys())) / len(bm25_model.idf.keys())
	scores = bm25_model.get_scores(query_dict, average_idf)
	return scores

"""
Write the query and all document scores in a common file holding all queries 
scored so far.

params: scores(the list of scores), docs(the list of documents), q(space-separated query)
return:
TODO: include all document scores? scores over a certain threshold? top n 
documents?
"""
<<<<<<< HEAD
def write_to_file(scores, docs, q, k):
=======
def write_to_file(scores, docs, q):
>>>>>>> 15d648cbfdb5aec698ff3667d6e94a5147f5613a
	if not os.path.exists(BM25FOLDER):
		os.makedirs(BM25FOLDER)
	bm25_file = open(BM25FOLDER+"bm25.csv", "a+")
	t = time.localtime()
	verbose_time = time.asctime(t)
	bm25_file.write(verbose_time+"\n")
	query = " ".join(q)
	output = "query, "+" ".join(q)+"\n"
	for i in range(0, len(scores)):
		scores[i] = (scores[i], docs[i])
	scores = sorted(scores, key=lambda tup:tup[0], reverse=True)
<<<<<<< HEAD
	for i in range(0, min(k, len(scores))):
=======
	for i in range(0, len(scores)):
>>>>>>> 15d648cbfdb5aec698ff3667d6e94a5147f5613a
		output+=scores[i][1]+", "+str(scores[i][0])+"\n"
	bm25_file.write(output)
	bm25_file.close()
	return 1

bm_25()