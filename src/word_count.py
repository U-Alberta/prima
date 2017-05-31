#!/usr/bin/python
from cStringIO import StringIO
import linecache
import glob
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
#from pdfminer.converter import TextConverter
#from pdfminer.layout import LAParams
#from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
#from pdfminer.pdfpage import PDFPage
import sys

WORDCOUNTFOLDER = "processed/word_count/"

# TODO: other file types? right now this works on txt, pdf
def word_count():
	if len(sys.argv) != 2:
		glob.error("17", ["word_count", ""])
		return -1
	param = sys.argv[1]
	param = param.strip("/")
	depth = len(param.split("/"))
	try:
		n = get_n(depth, param)
	except:
		glob.error("4", ["word_count", ""])
		return -1
	try:
		output = str(n)
		write_to_file(output, param)
	except:
		glob.error("14", ["word_count", ""])
		return -1
	try:
		param = sys.argv[1]
		glob.insert_to_db("word_count", param, output)
	except:
		glob.error("16", ["word_count", ""])
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
			glob.error("5", ["word_count", "", "collection", path])
			return -1
	elif depth == 2:
		try:
			n = count_item(path)
		except:
			glob.error("5", ["word_count", "", "item", path])
			return -1
	elif depth == 3:
		try:
			n = count_file(path)
		except:
			glob.error("5", ["word_count", "", "file", path])
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
	"""
	This is for handling pdf type files. Still not working great.
	if len(path.split(".pdf")) == 2:
		line = glob.convert_pdf_to_txt(path)
		n+=count_line(line)
	"""
	#elif len(path.split(".txt")) == 2:
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
				if term[0] not in glob.PUNC.keys():
					n+=1
	except:
		pass
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

word_count()