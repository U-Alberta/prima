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
        cols = range(0, k)
        shared.write_to_file(ck, cols, LDAFOLDER, "lda.csv")
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
    lda = models.LdaModel(corpus=corpus, id2word=dictionary, num_topics=k)
    ck = []
    for i in range(0, k):
        ck.append([])
    for i in range(0, lda.num_topics):
        topic = lda.print_topic(i, topn=k).split(" + ")
        [ck[i].append(word) for word in topic] 
    return ck

if __name__ == '__main__':
    lda()
