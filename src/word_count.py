#!/usr/bin/python
import glob
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
import sys

WORDCOUNTFOLDER = "processed/word_count/"
PATH = "source"

def word_count():
	if len(sys.argv) != 1:
		glob.error("17", ["word_count", ""])
		return -1
	try:
		output = count_collection()
	except:
		glob.error("4", ["word_count", ""])
		return -1
	try:
		write_to_file(output)
	except:
		glob.error("14", ["word_count", ""])
		return -1
	try:
		glob.insert_to_db("word_count", "", "Finished")
	except:
		glob.error("16", ["word_count", ""])
		return -1
	return 1

"""
Iterate through all the folders in the collection and call the next lower 
function (collection calls item which calls file which calls line).
"""
def count_collection():
	output = ""
	n = 0
	for doc_path in os.listdir(PATH):
		tup = count_item(PATH+"/"+doc_path)
		n+=tup[0]
		output+=tup[1]
	return PATH+", "+str(n)+"\n"+output

def count_item(path):
	output = ""
	n = 0
	for doc_path in os.listdir(path):
		tup = count_file(path+"/"+doc_path)
		n+=tup[0]
		output+=tup[1]
	return n, path+", "+str(n)+"\n"+output

def count_file(path):
	n = 0
	if len(path.split(".pdf")) == 2:
		line = glob.convert_pdf_to_txt(path)
		n+=count_line(line)
	elif len(path.split(".txt")) == 2:
		doc = open(path, "r")
		for line in doc:
			n+=count_line(line)
		doc.close()
	else:
		print("Incompatible file type {}".format(file))
		pass
	return n, path+", "+str(n)+"\n"

"""
When count_line is called, tokenize the line, remove symbols and count the 
words.
"""
def count_line(line):
	n = 0
	try:
		sentence_list = sent_tokenize(line)
		for sentence in sentence_list:
			for term in word_tokenize(sentence):
				if term[0] not in glob.PUNC.keys():
					n+=1
	except:
		pass
	return n

"""
Write the word count values to the file processed/word_count/word_count.txt.
"""
def write_to_file(output):
	if not os.path.exists(WORDCOUNTFOLDER):
		os.makedirs(WORDCOUNTFOLDER)
	outfile = open(WORDCOUNTFOLDER+"/word_count.csv", "w")
	outfile.write("document/directory, count\n")
	outfile.write(output)
	outfile.close()

word_count()








"""
This determines whether the user wanted collection, item, file, or line-level 
word count by checking how many '/'s were used in the input path.


Old function from old usage of this
"""
def get_count(depth, path):
	if depth == 1:
		try:
			n = count_collection(path)
		except:
			glob.error("5", ["word_count", ""], "collection", path)
			return -1
	elif depth == 2:
		try:
			n = count_item(path)
		except:
			glob.error("5", ["word_count", ""], "item", path)
			return -1
	elif depth == 3:
		try:
			n = count_file(path)
		except:
			glob.error("5", ["word_count", ""], "file", path)
			return -1
	elif depth == 4:
		try:
			lineno = int(path.split("/")[-1])
			tmp = path.split("/")[:-1]
			newpath = "/".join(tmp)
			line = linecache.getline(newpath, lineno)
		except:
			pass
		try:
			n = count_line(line)
		except:
			glob.error("6", ["word_count", "", lineno, newpath])
			return -1
	else:
		glob.error("18", ["word_count", "", path])
		return -1
	return n