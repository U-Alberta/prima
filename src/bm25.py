#!/usr/bin/python
from gensim import corpora, summarization
import os
import shared
import sys

BM25FOLDER = "processed/bm25/"

def bm_25():
	if len(sys.argv) < 2:
		shared.error("11", ["bm25", ""])
		return -1
	q = sys.argv[1:]
	try:
		texts, documents = shared.build_texts("bm25")
	except:
		shared.error("0", ["bm25", q])
		return -1
	try:
		scores = score(texts, q)
	except:
		shared.error("1", ["bm25", q])
		return -1
	try:
		write_to_file(scores, documents, q)
	except:
		shared.error("8", ["bm25", q])
	try:
		shared.insert_to_db("bm25", "", "Finished")
	except:
		shared.error("10", ["bm25", ""])
		return -1
	return 1


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
def write_to_file(scores, docs, q):
  if not os.path.exists(BM25FOLDER):
    os.makedirs(BM25FOLDER)
  bm25_file = open(BM25FOLDER+"bm25.csv", "a+")
  output = "query, "+ " ".join(q)+"\n"
  for i in range(0, len(docs)):
  	output+=docs[i]+", "+str(scores[i])+"\n"
  bm25_file.write(output)
  bm25_file.close()
  return 1

bm_25()