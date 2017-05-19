#!/usr/bin/python
import datetime
import linecache
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
import sqlite3
import sys

PUNC = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, "*":0, \
	"(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0, 	"}":0, \
	"|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, ">":0, "/":0, "?":0}
WORDCOUNTFOLDER = "processed/word_count/"
HISTDB = "processed/hist.db"

# TODO: other file types?
def word_count():
	if len(sys.argv) != 2:
		print("Invalid number of command line arguments")
		print("Usage: ~/word_count.sh dir[/item/file/line]")
		return -1
	param = sys.argv[1]
	param = param.strip("/")
	depth = len(param.split("/"))
	"""
	Depending on the file depth of the path given by the user (to a 
	collection, item, etc), compute n.
	"""
	try:
		n = get_n(depth, param)
	except:
		print("Error counting words")
		return -1
	"""
	Once n has been sucessfully computed, create a file in the appropriate 
	place (name_outfile) and save the value of n in there.
	"""
	try:
		output = str(n)
		write_to_file(output, param)
	except:
		print("Error saving result to file")
		return -1
	try:
		param = sys.argv[1]
		insert_to_db(param, output)
	except:
		print("Error saving to history database")
		return -1
	return 1

"""
This determines whether the user wanted collection, item, file, or line-level 
word count by checking how many '/'s were used in the input path.
"""
def get_n(depth, path):
	if depth == 1:
		try:
			n = count_collection(path)
		except:
			print("Error counting words in collection {}".format(command))
			return -1
	elif depth == 2:
		try:
			n = count_item(path)
		except:
			print("Error counting words in item {}".format(command))
			return -1
	elif depth == 3:
		try:
			n = count_file(path)
		except:
			print("Error counting words in file {}".format(command))
			return -1
	elif depth == 4:
		try:
			lineno = int(path.split("/")[-1])
			tmp = path.split("/")[:-1]
			newpath = "/".join(tmp)
			line = linecache.getline(newpath, lineno)
		except:
			print("Invalid path given")
			return -1
		try:
			n = count_line(line)
		except:
			print("Error counting words in line {} of {}".format(lineno, newpath))
			return -1
	else:
		print("Invalid path depth")
		return -1
	return n

"""
If the user gave something higher than a line, iterate through objects and 
call the next lower function (collection calls item which calls file which 
calls line).
"""
def count_collection(path):
	n = 0
	for doc_path in os.listdir(path):
		n+=count_item(path+"/"+doc_path)
	return n

def count_item(path):
	n = 0
	for doc_path in os.listdir(path):
		n+=count_file(path+"/"+doc_path)
	return n

def count_file(path):
	n = 0
	doc = open(path, "r")
	for line in doc:
		n+=count_line(line)
	doc.close()
	return n

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
				if term[0] not in PUNC.keys():
					n+=1
	except:
		print("Error counting words in line {}, moving on".format(line))
	return n

"""
Write the word count value to the generated outfilename in the 
processed/word_count folder.
"""
def write_to_file(output, path):
	outfilename = name_outfile(path)
	outfile = open(outfilename, "w")
	outfile.write(output)
	outfile.close()

"""
With the path given, create a unique file name for each potential input 
line, file, item, or collection. If the directory processed/word_count 
doesn't exist, create it so we can add the output file to it later.
"""
def name_outfile(path):
	path = path.split("/")
	clean_path = []
	for directory in path:
		directory = "".join(directory.split("_"))
		directory = directory.split(".")[0]
		if len(clean_path) == 3:
			directory = "line"+directory
		clean_path.append(directory)
	outfile = "_".join(clean_path)
	outfile = WORDCOUNTFOLDER+outfile+".txt"
	if not os.path.exists(WORDCOUNTFOLDER):
		os.makedirs(WORDCOUNTFOLDER)
	return outfile

"""
Insert the command used, output, and time run to the history database.
"""
def insert_to_db(param, output):
	time = datetime.datetime.now()
	line = ("word_count", param, output, time,)
	conn = sqlite3.connect(HISTDB)
	c = conn.cursor()
	c.execute("INSERT INTO History VALUES(?,?,?,?)", line)
	conn.commit()
	conn.close()
	return 1

word_count()