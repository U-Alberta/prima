#!/usr/bin/python
from gensim import corpora, models
import shared
import sys

LSIFOLDER = "processed/lsi/"

def lsi():
	if len(sys.argv) != 2:
		shared.error("11", ["lsi", ""])
		return -1
	k = int(sys.argv[1])
	try:
		texts, documents = shared.build_texts("lsi")
	except:
		shared.error("0", ["lsi", k])
		return -1
	try:
		ck = get_lsi(texts, k)
	except:
		shared.error("4", ["lsi", k])
		return -1
	try:
		shared.write_to_file(ck, documents, LSIFOLDER, "lsi.csv")
	except:
		shared.error("8", ["lsi", k])
		return -1
	try:
		shared.insert_to_db("lsi", k, "Finished")
	except:
		shared.error("10", ["lsi", k])
		return -1
	return 1

"""
Use the gensim library to generate an lsi matrix.

params: texts (created by shared.build_texts), k (number of dimensions)
return: ck (lsi reduced matrix)
"""
def get_lsi(texts, k):
	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]
	tfidf = models.TfidfModel(corpus)
	corpus_tfidf = tfidf[corpus]
	lsi = models.LsiModel(corpus, id2word=dictionary, num_topics=k)
	corpus_lsi = lsi[corpus_tfidf]
	ck = []
	for i in range(0, len(corpus_lsi[0])):
		ck.append([])
	for row in corpus_lsi:
		for i in range(0, len(row)):
			ck[i].append(row[i][1])
	return ck

lsi()