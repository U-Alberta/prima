#!/usr/bin/python
"""
This file holds functions and variables used in multiple files to reduce 
redundancies in the code.
"""
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
Parse through all the documents in the corpus, generating a list of words and 
documents.
Called by lda.py, and lsi.py.
"""
def build_texts():
  texts = []
  documents = []
  for item in sorted(os.listdir("source")):
    itemid = "".join(item.split("_"))
    for file in sorted(os.listdir("source/"+item)):
      fileid = file.split(".")[0]
      docid = "source/"+itemid+"/"+fileid
      try:
        doc = open("source/"+item+"/"+file, "r")
        documents.append(docid)
        doc_text = []
        for line in doc:
          sentence_list = sent_tokenize(line.decode("utf-8"))
          for sentence in sentence_list:
            for term in word_tokenize(sentence):
              if term[0] not in PUNC.keys():
                try:
                  term = term.lower()
                  doc_text.append(term)
                except:
                  pass
        texts.append(doc_text)
      except:
        print("Error opening document {}".format(docid))
  return texts, documents

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
params = [command, command line parameters, ..]
"""
def error(code, params, val1="", val2=""):
  code_map = {
    "0":"Error building text",
    "1":"Error calculating tfidf values",
    "2":"Error calling c functions for hashing",
    "3":"Error connecting to database {}".format(val1),
    "4":"Error counting words",
    "5":"Error counting words in {} {}".format(val1, val2),
    "6":"Error counting words in line {} of {}".format(val1, val2),
    "7":"Error getting {} matrix".format(params[0]),
    "8":"Error generating centroids",
    "9":"Error generating inverted index",
    "10":"Error generating {}-shingles".format(val1),
    "11":"Error generating random seed documents",
    "12":"Error opening document {}".format(val1),
    "13":"Error running reclustering algorithm",
    "14":"Error saving result to file(s)",
    "15":"Error saving to database {}".format(val1),
    "16":"Error saving to history database {}".format(HISTDB),
    "17":"Invalid number of command line arguments\nCheck usage in README.md",
    "18":"Invalid path {}".format(val1)}
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

"""
Write the newly created matrix ck to a csv file in the processed/lsi folder.
Called by lsi.py, and lda.py.
"""
def write_to_file(ck, docs, folder, file):
  df = pd.DataFrame(ck, columns=docs)
  if not os.path.exists(folder):
    os.makedirs(folder)
  df.to_csv(folder+file)