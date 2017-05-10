# prima
Personal Research Management for the IA

## Setup
1. Clone this repository to somewhere in your file system
2. Setup a path to /prima/src and run
  >
    $ chmod u+x ~/path/to/prima/src/*.py
3. Create a directory for your different collections to be save in and a new directory within this for each collection to be downloaded
4. Once inside the directory for a collection, initialize the files by running 
  >
    $ ~/path/to/prima/tools/init.sh
5. To download a collection into the auto-generated source/ folder, run the following where **collection_name** is a valid id for a collection in archive.org (for example [this](https://archive.org/details/toronto) collection would use collection_name toronto)
  >
    $ ~/path/to/prima/tools/fetch_collection.sh collection_name 

6. After completeing steps 1-5, run the following to get stats on your collection where **tool** is one of the options below
  >
    $ ~/path/to/prima/tools/tool 

## Tools

### word_count.sh
Given a directory depth starting from source (counts the entire collection) and going down to /source/item/file/lineno this will count all words in the readable files in the input directory. For example, running 
  >
    $ ~/path/to/prima/tools/word_count.sh source/item/filename.txt
will create a file in your collection directory/processed/word_count called source_item_filename.txt with the word count of that document. Running
  >
    $ ~/path/to/prima/tools/word_count.sh source
will create a file in your collection directory/processed/word_count called source.txt with the word count of all documents in the source collection.

### tfidf.sh: 
Taking no input, this calculates the tf, df, and tfidf of all the documents in the collection in the source/ folder. These values are then saved in your collection directory/processed/tfidf as df.txt (holding tab-separated terms and their document frequencies), tf.txt (tab-separated term document pairs and their term frequencies), and tfidf.txt (tab-separated term document pairs and their tf-idf values). This also creates a SQLite database in /processed/inverted_index.db which is used for later calculations but can be accessed. The database contains two tables; one holding tokens, their id's and document frequency and another holding token postings in documents as well as tf-idf values.

idf was calculated using log(N/df) where N is the size of documents in the corpus (corpus here is defined as the whole collection and N is the total number of documents read), tf is the term frequency of a term in a document, and df is the document frequency of a term in the corpus.

### lsi.sh: 
Taking no input, this builds a low-rank approximation of a term document matrix for all the documents in the collection. This matrix is then saved in your collection  directory/processed/lsi/lsi.csv. (TODO: take k as input? like the user can specify what size matrix they want?)

### lda.sh: TODO
