#!/usr/bin/python
import os
import shared
import sys
import time

MINHASHFOLDER = "processed/min_hash/"

def min_hash_sim():
    if len(sys.argv) == 2:
        doc = sys.argv[1]
        k = 10.0
    elif len(sys.argv) == 3:
        doc = sys.argv[1]
        k = float(sys.argv[2])
    else:
        shared.error("11", ["min_hash_sim", ""])
        return -1
    try:
        docid = get_docid(doc)
    except:
        shared.error("5", ["min_hash_sim", ""], "docname")
        return -1
    try:
        dup_docs = get_document_list(docid)
    except:
        shared.error("5", ["min_hash_sim", k], "closest duplicate documents")
        return -1
    try:
        write_to_file(dup_docs, docid, k)
    except:
        shared.error("8", ["min_hash_sim", k])
        return -1
    try:
        shared.insert_to_db("min_hash_sim", k, "Finished")
    except:
        shared.error("10", ["min_hash_sim", k])
        return -1
    return 1

def get_docid(doc):
    docid = doc.split(".")[0]
    docid = docid.split("/")
    for i in range(0, len(docid)):
        folder = docid[i]
        folder = "".join(folder.split("_"))
        docid[i] = folder
    docid = "/".join(docid)
    return docid

def get_document_list(doc):
    docs_list = []
    doc_pos = 0
    hashes = 0
    file = open(MINHASHFOLDER+"min_hash.csv", "r")
    time_line = file.readline()
    docs_line = file.readline()
    docs_line = docs_line.split(", ")
    docs_line[-1] = docs_line[-1].strip("\n")
    for i in range(1, len(docs_line)):
        docs_list.append((docs_line[i], 0))
        if docs_line[i] == doc:
          doc_pos = i-1
    for line in file:
        hash_vals = line.split(", ")
        hash_vals = hash_vals[1:]
        hash_vals[-1] = hash_vals[-1].strip("\n")
        doc_hash_val = hash_vals[doc_pos]
        for i in range(0, len(hash_vals)):
            if hash_vals[i] == doc_hash_val:
                tmp = docs_list[i]
                docs_list[i] = (tmp[0], tmp[1]+1)
        hashes+=1
    docs_list = docs_list[:doc_pos]+docs_list[doc_pos+1:]
    for i in range(0, len(docs_list)):
        tmp = docs_list[i]
        similarity = tmp[1]/hashes
        docs_list[i] = (tmp[0], similarity)
    docs_list = sorted(docs_list, key=lambda tup:tup[1], reverse=True)
    return docs_list

def write_to_file(docs, docid, k):
    if not os.path.exists(MINHASHFOLDER):
        os.makedirs(MINHASHFOLDER)
    file = open(MINHASHFOLDER+"min_hash_sim.csv", "a+")
    t = time.localtime()
    verbose_time = time.asctime(t)
    file.write(docid+", "+verbose_time+"\n")
    if k < 1: # Write documents with a score higher than k
        i = 0
        while i < len(docs):
            if docs[i][1] > k:
                row = docs[i][0]+", "+str(docs[i][1])+"\n"
                file.write(row)
            else:
                i = len(docs)
            i+=1
    else: # Write k documents
        k = int(k)
        if len(docs) < k:
            print("Warning: number of documents to return higher than number of "\
            "documents in the collection")
        for i in range(0, min(k, len(docs))):
            row = docs[i][0]+", "+str(docs[i][1])+"\n"
            file.write(row)
    file.close()
    return 1

if __name__ == '__main__':
    min_hash_sim()