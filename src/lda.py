#!/usr/bin/python
from gensim import corpora, models
import shared
import sys

LDAFOLDER = "processed/lda/"

def lda():
    if len(sys.argv) == 1:
        k = 100 # Default dimensions is 100
    elif len(sys.argv) == 2:
        k = int(sys.argv[1])
    else:
        shared.error("11", ["lda", ""])
        return -1
    try:
        texts, documents = shared.build_texts("lda")
    except:
        shared.error("0", ["lda", k])
        return -1
    try:
        ck = get_lda(texts, k)
    except:
        shared.error("4", ["lda", k])
        return -1
    try:
        shared.write_to_file(ck, documents, LDAFOLDER, "lda.csv")
    except:
        shared.error("8", ["lda", k])
        return -1
    try:
        shared.insert_to_db("lda", k, "Finished")
    except:
        shared.error("10", ["lda", k])
        return -1
    return 1

"""
Use the gensim library to generate an lda matrix.

params: texts (created by shared.build_texts), k (number of dimensions)
return: ck (lda reduced matrix)
"""
def get_lda(texts, k):
    dictionary = corpora.Dictionary(texts)
    corpus = [dictionary.doc2bow(text) for text in texts]
    lda = models.LdaModel(corpus, id2word=dictionary, num_topics=k)
    corpus_lda = lda[corpus]
    ck = []
    for i in range(0, len(corpus_lda[0])):
        ck.append([])
    for row in corpus_lda:
        for i in range(0, len(row)):
            ck[i].append(row[i][1])
    return ck

if __name__ == '__main__':
    lda()