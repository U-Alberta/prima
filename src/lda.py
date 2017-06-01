#!/usr/bin/python
from gensim import corpora, models
import glob
import sys

LDAFOLDER = "processed/lda/"

# TODO: allow to work on specific directories like word_count?
def lda():
	if len(sys.argv) != 2:
		glob.error("17", ["lda", ""])
		return -1
	k = int(sys.argv[1])
	try:
		texts, documents = glob.build_texts("lda")
	except:
		glob.error("0", ["lda", k])
		return -1
	try:
		ck = get_lda(texts, k)
	except:
		glob.error("7", ["lda", k])
		return -1
	try:
		glob.write_to_file(ck, documents, LDAFOLDER, "lda.csv")
	except:
		glob.error("14", ["lda", k])
		return -1
	try:
		glob.insert_to_db("lda", k, "Finished")
	except:
		glob.error("16", ["lda", k])
		return -1
	return 1

"""
Use the gensim library to generate an lda matrix.
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

lda()