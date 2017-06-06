#!/usr/bin/python
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
import shared
import sys

WORDCOUNTFOLDER = "processed/word_count/"
PATH = "source"

def word_count():
	if len(sys.argv) != 1:
		shared.error("11", ["word_count", ""])
		return -1
	try:
		output = count_collection()
	except:
		shared.error("3", ["word_count", ""])
		return -1
	try:
		write_to_file(output)
	except:
		shared.error("8", ["word_count", ""])
		return -1
	try:
		shared.insert_to_db("word_count", "", "Finished")
	except:
		shared.error("10", ["word_count", ""])
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
		line = shared.convert_pdf_to_txt(path)
		n+=count_line(line)
	elif len(path.split(".txt")) == 2:
		doc = open(path, "r")
		for line in doc:
			n+=count_line(line, path)
		doc.close()
	else:
		print("Warning: incompatible file type {}".format(file))
		pass
	return n, path+", "+str(n)+"\n"

"""
When count_line is called, tokenize the line, remove symbols and count the 
words.
"""
def count_line(line, path):
	n = 0
	try:
		sentence_list = sent_tokenize(line)
		for sentence in sentence_list:
			for term in word_tokenize(sentence):
				if term[0] not in shared.PUNC.keys():
					n+=1
	except:
		print("Warning: couldn't read line in file {}".format(path))
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