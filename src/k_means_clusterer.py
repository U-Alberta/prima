#!/usr/bin/python
import math
import os
import random
import shared
import sqlite3
import sys

KMEANSFOLDER = "processed/k_means/"
IIDB = "processed/inverted_index.db"

def k_means_clusterer():
	if len(sys.argv) != 2:
		shared.error("11", ["k_means_clusterer", ""])
		return -1
	k = sys.argv[1]
	k = int(k)
	"""
	Do we want to let users specify seeds?
	"""
	"""
	if len(sys.argv) > 3:
		seeds = sys.argv[3:]
		if len(seeds) != k:
			print("k doesn't match number of seeds given")
			return -1
	else: 
	"""
	try:
		texts, documents = shared.build_texts("k_means_clusterer")
	except:
		shared.error("0", ["k_means_clusterer", ""])
		return -1
	try:
		tfidf, raw_tf, dictionary = shared.get_tfidf(texts)
	except:
		shared.error("1", ["k_means_clusterer", ""])
		return -1
	try:
		seeds = gen_seeds(k, documents)
	except:
		shared.error("5", ["k_means_clusterer", k], "random seed documents")
		return -1
	try:
		inverted_index = build_inverted_index(tfidf, raw_tf, dictionary, documents)
	except:
		shared.error("5", ["k_means_clusterer", k], "inverted_index")
		return -1	
	try:
		centroids = get_seed_vector(seeds, inverted_index, dictionary, documents)
	except:
		shared.error("5", ["k_means_clusterer", k], "centroids")
		return -1
	"""
	Loop through reclustering documents and recalculating centroids until the 
	clusters don't change anymore.
	"""
	while True:
		try:
			cluster1 = get_cluster(centroids, documents, inverted_index, dictionary)
			centroid1 = update_centroids(cluster1)
			cluster2 = get_cluster(centroid1, documents, inverted_index, dictionary)
		except:
			shared.error("7", ["k_means_clusterer", k])
			return -1
		if cluster1 == cluster2:
			try:
				write_to_file(cluster2)
				break
			except:
				shared.error("8", ["k_means_clusterer", k])
				return -1
		else:
			centroids = update_centroids(cluster2)
	try:
		shared.insert_to_db("k_means_clusterer", k, "Finished")
	except:
		shared.error("10", ["k_means_clusterer", k])
	return 1

"""
If no seeds are given, this randomly selects k seeds from the database.
"""
def gen_seeds(k, docs):
	seeds = []
	while k > 0:
		d = random.choice(docs)
		if d not in seeds:
			seeds.append(d)
		k-=1
	return seeds

"""
Uses the output from the glob commands above to build an inverted index.
"""
def build_inverted_index(tfidf, raw_tf, dictionary, documents):
	inverted_index = {}
	for i in range(0, len(documents)):
		doc = documents[i]
		postings = raw_tf[i]
		for j in range(0, len(postings)):
			token = dictionary[postings[j][0]]
			if token not in inverted_index.keys():
				inverted_index[token] = {"postings":{doc:(postings[j][1], tfidf[i][j][1])}}
			else:
				inverted_index[token]["postings"][doc] = (postings[j][1], tfidf[i][j][1])
	return inverted_index

"""
Generates the vectors (ltc) for the seed documents to make initial centroids.
"""
def get_seed_vector(seeds, inverted_index, tokens, documents):
	"""
	seed vector uses ltc weighting: tf=1+log(tf t,d), df=log(N/df t), 
	normalization=1/sqrt(w1^2+w2^2+w3^2+...+wM^2)
	"""
	centroids = []
	N = len(documents)
	c_id = 0
	for s in seeds:
		vector = []
		for i in range(0, len(tokens)):
			tfidf = 0
			t = tokens[i]
			if s in inverted_index[t]["postings"].keys():
				tfidf = inverted_index[t]["postings"][s][1]
			vector.append(tfidf)
		weights = 0
		for v in vector:
			weights+=v**2
		normalization = 1/math.sqrt(weights)
		_ = 0
		while _ < len(vector):
			v = vector[_]
			v = v/normalization
			vector[_] = v
			_+=1
		centroids.append((vector, c_id))
		c_id+=1
	return centroids

"""
Calculates a document vector based on lnc values.
"""
def get_document_vector(inverted_index, tokens, d):
	"""
	doc vector uses lnc: tf=1+log(tf t, d), df=1, 
	normalization=1/sqrt(w1^2+w2^2+w3^2+...+wM^2)
	"""
	d_vector = []
	for i in range(0, len(tokens)):
		t = tokens[i]
		tf = 0
		if d in inverted_index[t]["postings"].keys():
			tf = inverted_index[t]["postings"][d][0]
		d_vector.append(tf)
	weights = 0
	for v in d_vector:
		weights+=v**2
	normalization = 1/math.sqrt(weights)
	_ = 0
	while _ < len(d_vector):
		v = d_vector[_]
		v = v/normalization
		d_vector[_] = v
		_+=1
	return d_vector

def dot_product(s, d):
	i = 0
	product = 0
	while i < len(d):
		product+=d[i]*s[i]
		i+=1
	return product

def length_product(s, d):
	len_d = 0
	len_s = 0
	i = 0
	while i < len(d):
		len_d+=d[i]**2
		len_s+=s[i]**2
		i+=1
	len_d = math.sqrt(len_d)
	len_s = math.sqrt(len_s)
	return len_d*len_s

"""
Calculates the distance between two vectors according to cosine similarity 
algorithm.
"""
def sd_distance(s, d):
	num = dot_product(s, d)
	den = length_product(s, d)
	dist = num/den
	return dist

"""
Assigns every document in the collection to the closest cluster to it.
"""
def get_cluster(centroids, docs, inverted_index, tokens):
	temp = []
	for d in docs:
		d_vector = get_document_vector(inverted_index, tokens, d)
		distances = []
		for s in centroids:
			s_vector = s[0]
			dist = sd_distance(s_vector, d_vector)
			distances.append((dist, s[1], d_vector, d))
		distances.sort(key=lambda tup: tup[0], reverse=True)
		temp.append(distances[0])
	cluster = {}
	for tup in temp:
		if tup[1] in cluster.keys():
			cluster[tup[1]].append((tup[2], tup[3]))
		else:
			cluster[tup[1]] = [(tup[2], tup[3])]
	return cluster

"""
After reclustering, this updates the centroids of the new clusters.
"""
def update_centroids(cluster):
	u = []
	for i in cluster:
		w = cluster[i]
		v_sum = []
		for _ in range(0, len(w[0][0])):
			j = 0
			s = 0
			while j < len(w):
				s+=w[j][0][_]
				j+=1
			v_sum.append(s/len(w))
		u.append((v_sum, i))
	return u

def write_to_file(k_clusters):
	if not os.path.exists(KMEANSFOLDER):
		os.makedirs(KMEANSFOLDER)
	kmeans_file = open(KMEANSFOLDER+"k_means.csv", "w")
	for cluster in k_clusters.keys():
		output = ""
		for file in k_clusters[cluster]:
			output+=str(file[1])+", "
		output = output[:len(output)-2]+"\n"
		kmeans_file.write(output)
	kmeans_file.close()
	return 1

k_means_clusterer()