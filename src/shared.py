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
SHINGLES = 3

"""
Parse through all the documents in the corpus, generating a list of words and 
documents.

called by: lda.py, lsi.py, min_hash.py, and tfidf.py.
params: mode (which function is calling this)
return: s (a set of shingles) or texts (a list of all the terms in all the 
    documents) and documents(list of documents)
"""
def build_texts(mode, k=0):
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
                    doc = open(path, "r")
                    doccounter+=1
                else:
                    print("Warning: incompatible file type {}".format(file))
                    pass
                documents.append(docid)
                doc_text = []
                if mode == "min_hash": shingle = prep_shingle(k)
                for line in doc:
                    sentence_list = sent_tokenize(line.decode("utf-8"))
                    for sentence in sentence_list:
                        for term in word_tokenize(sentence):
                            if term[0] not in PUNC.keys():
                                try:
                                    term = str(term.lower())
                                    if mode == "min_hash":
                                        shingle, s = min_hash_subfxn(doccounter, s, shingle, term, k)
                                    doc_text.append(term)
                                except:
                                    pass
                texts.append(doc_text)
            except:
                print("Warning: couldn't open document {}".format(docid))
    if mode == "min_hash": return s, documents
    else: return texts, documents

"""
gen_shingles, prep_shingles, and min_hash_subfxn are all used by min_hash. 
gen_shingles is called by min_hash. prep_shingles and min_hash_subfxn are 
called in build_texts only when mode="min_hash" to generate shingles rather 
than build a list of the text and documents.
"""
def gen_shingles(k):
    shingles =  build_texts("min_hash", k)
    return shingles

def prep_shingle(k):
    shingle = []
    for i in range(0, k):
        shingle.append("")
    return shingle

"""
params: doccounter (counter for documents for entering to the shingles db), 
s (list of shingles so far), shingle (list of shingles for that document),
term (current term)
return: shingle (list of shingles for that document), s (list of shingles so 
    far)
"""
def min_hash_subfxn(doccounter, s, shingle, term, k):
    for i in range(0, k):
        if shingle[i] == "":
            shingle[i] = term
            break
    if shingle[-1] != "":
        shingle_str = " ".join(shingle)
        s.append((doccounter, shingle_str))
        for i in range(0, k-1):
            shingle[i] = shingle[i+1]
        shingle[-1] = ""
    return shingle, s

"""
Write the newly created matrix ck to a csv file in the processed/lsi folder.

called by: lsi.py, and lda.py.
params: ck (new reduced matrix), docs (document list for columns), folder 
    (folder to be saved in), file (file to be saved in)
return:
"""
def write_to_file(ck, docs, folder, file):
    df = pd.DataFrame(ck, columns=docs)
    if not os.path.exists(folder):
        os.makedirs(folder)
    df.to_csv(folder+file)
    return 1

"""
Use the gensim library to calculate tfidf.

called by: k_means_clusterer.py, and tfidf.py
params: texts (created by shared.build_texts)
return: corpus_tfidf (a list of tfidf values), corpus (a list of term ids in 
    all the documents of the corpus), dictionary (a list of terms in the corpus)
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

called by: word_count.py, and tfidf.py.
params: path (the path to the pdf)
return: text (one line of text representing the entire pdf)
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
A list of all the possible errors that can be thrown by all the functions.

params: code (error code number), params ([command, command line arguments]), 
    val1 (empty unless needed for further information)
return:
"""
def error(code, params, val1=""):
    code_map = {
        "0":"Error building text",
        "1":"Error calculating {} values".format(val1),
        "2":"Error calling c functions for hashing",
        "3":"Error counting words",
        "4":"Error getting {} matrix".format(val1),
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

called by: all functions.
params: command (the function called), param (command line arguments), output 
(whether or not the function was successfully completed)
return:
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