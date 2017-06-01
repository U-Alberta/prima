#!/usr/bin/python
from gensim import corpora, models
import glob
import sys

LSIFOLDER = "processed/lsi/"

# TODO: allow to work on specific directories like word_count?
def lsi():
	if len(sys.argv) != 2:
		glob.error("17", ["lsi", ""])
		return -1
	k = int(sys.argv[1])
	try:
		texts, documents = glob.build_texts("lsi")
	except:
		glob.error("0", ["lsi", k])
		return -1
	#try:
	ck = get_lsi(texts, k)
	#except:
		#glob.error("7", ["lsi", k])
		#return -1
	try:
		glob.write_to_file(ck, documents, LSIFOLDER, "lsi.csv")
	except:
		glob.error("14", ["lsi", k])
		return -1
	try:
		glob.insert_to_db("lsi", k, "Finished")
	except:
		glob.error("16", ["lsi", k])
		return -1
	return 1

"""
Use the gensim library to generate an lsi matrix.
"""
def get_lsi(texts, k):
	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]
	tfidf = models.TfidfModel(corpus)
	corpus_tfidf = tfidf[corpus]
	lsi = models.LsiModel(corpus_tfidf, id2word=dictionary, num_topics=k)
	corpus_lsi = lsi[corpus_tfidf]
	ck = []
	for i in range(0, len(corpus_lsi[0])):
		ck.append([])
	for row in corpus_lsi:
		for i in range(0, len(row)):
			ck[i].append(row[i][1])
	return ck

lsi()