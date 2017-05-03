# prima
Personal Research Management for the IA

## Setup
1. Clone this repository to somewhere in your file system
2. Setup a path to /prima/src
3. Create a directory for your collections to be save in and a new directory within this for each collection to be downloaded
4. Once inside the directory for a collection, initialize the files by running 
  >
    ~/path/to/prima/tools/init.sh
5. To download a collection, run the following where **collection_name** is a valid id for a collection in archive.org
  >
    ~/path/to/prima/tools/fetch_collection.sh collection_name 

6. After completeing steps 1-5, run the following to get stats on your collection where **tool** is one of the options below
  >
    ~/path/to/prima/tools/tool 

## Tools
The tools available are:
* word_count.sh: given a directory depth starting from source (counts the entire collection) and going down to /source/item/file/lineno this will count all words in the input.
* tfidf.sh: TODO
* lsi.sh: TODO
* lda.sh: TODO
