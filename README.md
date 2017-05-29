# prima
Personal Research Management for the IA

## Setup
1. Clone this repository to somewhere in your file system.
2. This project uses the gensim library for some of the tools. You will need to download it from the [website](https://radimrehurek.com/gensim/)
3. Setup a path to /prima/src and run the following, replacing ~/path/to with your personal path to the prima repository
  >
    $ chmod u+x ~/path/to/prima/src/*.py
    $ chmod u+x ~/path/to/prima/tools/*.sh
4. To create the appropriate directories for your file system run the following commands where **project_name** is the desired file name for a collection to be saved in
  >
    $ ~/path/to/prima/tools/init_workspace.sh
    $ cd workspace
    $ ~/path/to/prima/tools/init_project.sh project_name
    $ cd project_name
    $ ~/path/to/prima/tools/init.sh
5. To download a collection into the auto-generated source/ folder, run the following where **collection_name** is a valid id for a collection in archive.org (for example [this](https://archive.org/details/toronto) collection would use collection_name=toronto)
  >
    $ ~/path/to/prima/tools/fetch_collection.sh collection_name 

6. After completing steps 1-5, run the following to get stats on your collection where **tool** is one of the options listed below
  >
    $ ~/path/to/prima/tools/tool 
7. For every new collection to be created, repeat step 3 lines 3-5 and step 4 with the new collection.

## Tools

### word_count.sh
Given a directory depth starting from source (counts the entire collection) and going down to /source/item/file/lineno this will count all words in the readable files in the input directory. For example, running 
  >
    $ ~/path/to/prima/tools/word_count.sh source/item/filename.txt
will create a file in your collection directory/processed/word_count called source_item_filename.txt with the word count of that document. Running
  >
    $ ~/path/to/prima/tools/word_count.sh source
will create a file called source.txt with the word count of all documents in the source collection.

### tfidf.sh: 
Taking no input, this calculates the tf, df, and tfidf of all the documents in the collection in the source/ folder. These values are then saved in your collection directory/processed/tfidf as df.txt (holding tab-separated terms and their document frequencies), tf.txt (tab-separated term document pairs and their term frequencies), and tfidf.txt (tab-separated term document pairs and their tf-idf values). This also creates a SQLite database in /processed/inverted_index.db which is used for later calculations but can be accessed by running the command
  >
    $ sqlite3 processed/inverted_index.db
The database contains two tables; one holding tokens, their id's and document frequency and another holding token postings in documents as well as tf-idf values.

idf was calculated using log(N/df) where N is the size of documents in the corpus (corpus here is defined as the whole collection and N is the total number of documents read), tf is the term frequency of a term in a document, and df is the document frequency of a term in the corpus.

### k_means_clusterer.sh:
Taking the number of clusters k as input, this clusters the documents in the corpus into k groups according to the k means algorithm. Vectors are weighted using lnc.ltc according to SMART notation. For example, running
  >
    $ ~/path/to/prima/tools/k_means_clusterer.sh 3
will classify the documents within the source/ folder into 3 clusters. The k clusters and their associated documents are saved in processed/kmeans/kmeans.txt as tab-separated cluster ids and lists of documents.

### lsi.sh: 
Taking k as input, this builds a low-rank approximation of a term document matrix  of size k for all the documents in the collection. This matrix is then saved in your collection  directory/processed/lsi/lsi.csv. For example, running
  >
    $ ~/path/to/prima/tools/k_means_clusterer.sh 100
will reduce the term-document matrix c into a k-by-k matrix and save it in lsi.csv.

### lda.sh: TODO

### min_hash.sh:
Taking no input (as of now), this compares documents in the source/ directory using the [MinHash algorithm](https://en.wikipedia.org/wiki/MinHash). These values are then saved in processed/min_hash/min_hash.csv as a table with columns labelled by document ids and rows corresponding to each different hash function used.
  >
    $ ~/path/to/prima/tools/min_hash.sh
