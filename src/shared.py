#!/usr/bin/python
"""
This file holds functions and variables used in multiple files to reduce 
redundancies in the code.
"""
from gensim import corpora, models
from cStringIO import StringIO
import datetime
import nltk.tokenize
from nltk.tokenize import sent_tokenize, word_tokenize
import os
import pandas as pd
from pdfminer.converter import TextConverter
from pdfminer.layout import LAParams
from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
from pdfminer.pdfpage import PDFPage
import sqlite3

PUNC = {"`":0, "~":0, "!":0, "@":0, "#":0 , "$":0, "%":0, "^":0, "&":0, "*":0, \
  "(":0, ")":0, "-":0, "_":0, "=":0, "+":0, "[":0, "]":0, "{":0,  "}":0, \
  "|":0, ";":0, ":":0, "'":0, '"':0, ",":0, "<":0, ".":0, ">":0, "/":0, "?":0, \
  "0":0, "1":0, "2":0, "3":0, "4":0, "5":0, "6":0, "7":0, "8":0, "9":0}
HISTDB = "processed/hist.db"
"""
Should we let the user specify this? I think we could have 3 as a default and 
if the user wants to change it they can in the arguments.
"""
SHINGLES = 3

"""
Parse through all the documents in the corpus, generating a list of words and 
documents.
Called by lda.py, lsi.py, min_hash.py, and tfidf.py.
"""
def build_texts(mode):
  texts = []
  documents = []
  s = []
  raw_df = {}
  doccounter = -1
  for item in sorted(os.listdir("source")):
    itemid = "".join(item.split("_"))
    for file in sorted(os.listdir("source/"+item)):
      fileid = file.split(".")[0]
      docid = "source/"+itemid+"/"+fileid
      path = "source/"+item+"/"+file
      try:
        if len(path.split(".pdf")) == 2:
          line = convert_pdf_to_txt(path)
          doc = [line]
          doccounter+=1
        elif len(path.split(".txt")) == 2:
          doc = open("source/"+item+"/"+file, "r")
          doccounter+=1
        #elif path[len(path)-8:] == "_marc.xml":
        	#doc = read_marc(path)
        else:
          print("Incompatible file type {}".format(file))
          pass
        documents.append(docid)
        doc_text = []
        if mode == "min_hash": shingle = prep_shingle()
        for line in doc:
          sentence_list = sent_tokenize(line.decode("utf-8"))
          for sentence in sentence_list:
            for term in word_tokenize(sentence):
              if term[0] not in PUNC.keys():
                try:
                  term = str(term.lower())
                  if mode == "min_hash":
                    shingle, s = min_hash_subfxn(doccounter, docid, s, shingle, term)
                  doc_text.append(term)
                except:
                  pass
        texts.append(doc_text)
      except:
        error("12", [mode, ""], docid)
  if mode == "min_hash": return s
  else: return texts, documents

#def read_marc(path):

"""
gen_shingles, prep_shingles, and min_hash_subfxn are all used by min_hash. 
gen_shingles is called by min_hash. prep_shingles and min_hash_subfxn are 
called in build_texts only when mode="min_hash" to generate shingles rather 
than build a list of the text and documents.
"""
def gen_shingles():
  shingles =  build_texts("min_hash")
  return shingles

def prep_shingle():
  shingle = []
  for i in range(0, SHINGLES):
    shingle.append("")
  return shingle

def min_hash_subfxn(doccounter, docid, s, shingle, term):
  for i in range(0, SHINGLES):
    if shingle[i] == "":
      shingle[i] = term
      break
  if shingle[-1] != "":
    shingle_str = " ".join(shingle)
    s.append((doccounter, docid, shingle_str))
    for i in range(0, SHINGLES-1):
      shingle[i] = shingle[i+1]
    shingle[-1] = ""
  return shingle, s

"""
Write the newly created matrix ck to a csv file in the processed/lsi folder.
Called by lsi.py, and lda.py.
"""
def write_to_file(ck, docs, folder, file):
  df = pd.DataFrame(ck, columns=docs)
  if not os.path.exists(folder):
    os.makedirs(folder)
  df.to_csv(folder+file)

"""
Use the gensim library to calculate tfidf.
Called by k_means_clusterer.py, and tfidf.py
"""
def get_tfidf(texts):
	dictionary = corpora.Dictionary(texts)
	corpus = [dictionary.doc2bow(text) for text in texts]
	tfidf = models.TfidfModel(corpus)
	corpus_tfidf = tfidf[corpus]
	return corpus_tfidf, corpus, dictionary

"""
Converts pdf text to a single string based on code here:
https://stackoverflow.com/questions/26494211/extracting-text-from-a-pdf-file-using-pdfminer-in-python
Called by word_count.py, and tfidf.py.
"""
def convert_pdf_to_txt(path):
  rsrcmgr = PDFResourceManager()
  retstr = StringIO()
  codec = 'utf-8'
  laparams = LAParams()
  device = TextConverter(rsrcmgr, retstr, codec=codec, laparams=laparams)
  fp = file(path, 'rb')
  interpreter = PDFPageInterpreter(rsrcmgr, device)
  password = ""
  maxpages = 0
  caching = True
  pagenos = set()
  for page in PDFPage.get_pages(fp, pagenos, maxpages=maxpages, \
  	password=password, caching=caching, check_extractable=True):
    interpreter.process_page(page)
  text = retstr.getvalue()
  fp.close()
  device.close()
  retstr.close()
  return text

"""
I list of all the possible errors that can be thrown by all the functions.
params = [command, command line parameters, ..]
"""
def error(code, params, val1="", val2=""):
  code_map = {
    "0":"Error building text",
    "1":"Error calculating {} values".format(params[0]),
    "2":"Error calling c functions for hashing",
    "3":"Error counting words",
    "4":"Error getting {} matrix".format(params[0]),
    "5":"Error generating {}".format(val1),
    "6":"Error generating {}-shingles".format(SHINGLES),
    "7":"Error running reclustering algorithm",
    "8":"Error saving result to file(s)",
    "9":"Error saving to database {}".format(val1),
    "10":"Error saving to history database {}".format(HISTDB),
    "11":"Invalid number of command line arguments\nCheck usage in README.md"}
  print(code_map[code])
  insert_to_db(params[0], params[1], "Error code: "+code)
  return 1

"""
Insert the command used, output, and time run to the history database.
Called by all functions.
"""
def insert_to_db(command, param, output):
  time = datetime.datetime.now()
  line = (command, param, output, time,)
  conn = sqlite3.connect(HISTDB)
  c = conn.cursor()
  c.execute("INSERT INTO History VALUES(?,?,?,?)", line)
  conn.commit()
  conn.close()
  return 1