#!/usr/bin/python
import datetime
import math
import os
import random
import sqlite3
import sys

KMEANSFOLDER = "processed/kmeans"
KMEANSFILE = "processed/kmeans/kmeans.txt"
HISTDB = "processed/hist.db"
IIDB = "processed/inverted_index.db"

def k_means_clusterer():
	if len(sys.argv) != 2:
		print("Wrong number of command line arguments")
		print("Usage: ~/k_means_clusterer k")
		return -1
	k = sys.argv[1]
	k = int(k)
	try:
		conn = sqlite3.connect(IIDB)
		c = conn.cursor()
	except:
		print("Error connecting to database {}".format(IIDB))
	# Do we want to let users specify seeds?
	#if len(sys.argv) > 3:
		#seeds = sys.argv[3:]
		#if len(seeds) != k:
			#print("k doesn't match number of seeds given")
			#return -1
	#else: 
	try:
		seeds = gen_seeds(k, c)
	except:
		print("Error generating random seed documents")
		return -1
	try:
		inverted_index, docs = build_inverted_index(c)
	except:
		print("Error generating inverted index")
		return -1
	try:
		centroids = get_seed_vector(seeds, inverted_index, c)
	except:
		print("Error generating centroids")
		return -1
	while True:
		try:
			cluster1 = get_cluster(centroids, docs, inverted_index, c)
			centroid1 = update_centroids(cluster1)
			cluster2 = get_cluster(centroid1, docs, inverted_index, c)
		except:
			print("Error running reclustering algorithm")
			return -1
		if cluster1 == cluster2:
			try:
				write_to_file(cluster2)
				break
			except:
				print("Error writing to file")
				return -1
			return 1
		centroids = update_centroids(cluster2)
	try:
		insert_to_db(k, cluster2)
	except:
		print("Error inserting to database {}".format(HISTDB))
	return 1

def get_N(c):
	c.execute("SELECT COUNT(DISTINCT doc_id) FROM Posting")
	N = c.fetchone()[0]
	return N

def get_tokens(c):
	tokens = []
	c.execute("SELECT DISTINCT token FROM Token")
	for row in c.fetchall():
		tokens.append(row[0])
	return tokens

# If no seeds are given, this randomly selects k seeds from the database.
def gen_seeds(k, c):
	seeds = []
	docs = []
	c.execute("SELECT DISTINCT doc_id FROM Posting")
	for row in c.fetchall():
		docs.append(row[0])
	while k > 0:
		d = random.choice(docs)
		docs.remove(d)
		seeds.append(d)
		k-=1
	return seeds

# Builds an inverted index from the db so we don't have to repeatedly query the 
# database to get document vectors.
def build_inverted_index(c):
	doc_id = []
	c.execute("SELECT DISTINCT doc_id FROM Posting ORDER BY doc_id")
	for row in c.fetchall():
		doc_id.append(row[0])
	inverted_index = {}
	for d in doc_id:
		token_id = []
		doc = (d,)
		c.execute("SELECT DISTINCT token_id FROM Posting WHERE doc_id=?", doc)
		for row in c.fetchall():
			token_id.append(row[0])
		for t_id in token_id:
			variables = (d,t_id)
			c.execute("SELECT t.token, p.tf, t.df FROM Posting p, Token t WHERE p.doc_id=? AND t.token_id=? AND t.token_id=p.token_id", variables)
			for row in c.fetchall():
				token = row[0]
				tf = row[1]
				df = row[2]
				if token in inverted_index.keys():
					inverted_index[token]["postings"][d] = tf
				else:
					inverted_index[token] = {"df":df, "postings":{d:tf}}
	return inverted_index, doc_id

# Generates the vectors (ltc) for the seed documents to make initial centroids.
def get_seed_vector(seeds, inverted_index, c):
	#seed vector uses ltc weighting: tf=1+log(tf t,d), df=log(N/df t), normalization=1/sqrt(w1^2+w2^2+w3^2+...+wM^2)
	centroids = []
	N = get_N(c)
	tokens = get_tokens(c)
	c_id = 0
	for s in seeds:
		vector = []
		for t in tokens:
			tf = 0
			if s in inverted_index[t]["postings"].keys():
				tf = inverted_index[t]["postings"][s]
				tf = 1+math.log10(tf)
			df = inverted_index[t]["df"]
			idf = math.log10(N/df)
			vector.append(tf*idf)
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

# Calculates a document vector based on lnc values.
def get_document_vector(inverted_index, d, c):
	#doc vector uses lnc: tf=1+log(tf t, d), df=1, normalization=1/sqrt(w1^2+w2^2+w3^2+...+wM^2)
	tokens = get_tokens(c)
	d_vector = []
	for t in tokens:
		tf = 0
		if d in inverted_index[t]["postings"].keys():
			tf = inverted_index[t]["postings"][d]
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

# Calculates the distance between two vectors according to cosine similarity 
# algorithm.
def sd_distance(s, d):
	num = dot_product(s, d)
	den = length_product(s, d)
	dist = num/den
	return dist

# Assigns every document in the collection to the closest cluster to it.
def get_cluster(centroids, docs, inverted_index, c):
	temp = []
	for d in docs:
		d_vector = get_document_vector(inverted_index, d, c)
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

# After reclustering, this updates the centroids of the new clusters
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
	kmeans_file = open(KMEANSFILE, "w")
	for cluster in k_clusters.keys():
		output = str(cluster)+":\t"
		for file in k_clusters[cluster]:
			output+=str(file[1])+", "
		output+="\n"
		kmeans_file.write(output)
	kmeans_file.close()
	return 1

def insert_to_db(k, cluster):
	output = "True"
	# Code to potentially insert to the history database the clusters created by 
	# this function. This could be a really long list though which is why I'm 
	# leaving it out for now.
	"""
	for c in cluster:
		output+="("
		for doc in cluster[c]:
			output+=doc[1]+", "
		output = output[:len(output)-2]+"), "
	output = output[:len(output)-2]
	"""
	time = datetime.datetime.now()
	line = ("k_means_clusterer", k, output, time,)
	conn = sqlite3.connect(HISTDB)
	c = conn.cursor()
	c.execute("INSERT INTO History VALUES(?,?,?,?)", line)
	conn.commit()
	conn.close()
	return 1

k_means_clusterer()