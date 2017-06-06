# prima
Personal Research Management for the IA

## Installation
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

6. After completing steps 1-5, run the following to get stats on your collection where **tool** is one of the options listed below with the appropriate parameters
  >
    $ ~/path/to/prima/tools/tool params
7. For every new collection to be created, repeat step 3 lines 3-5 and step 4 with the new collection before using any tools.

## Tools
Current available tools included in the prima are:
1. BM25

        $ ~/path/to/prima/tools/bm25.sh "prima query bm25"
2. K-means clustering

        $ ~/path/to/prima/tools/k_means_clusterer.sh k
3. Latent Dirichlet allocation

        $ ~/path/to/prima/tools/lda.sh k
4. Latent semantic indexing

        $ ~/path/to/prima/tools/lsi.sh k
5. MinHash

        $ ~/path/to/prima/tools/min_hash.sh
        $ ~/path/to/prima/tools/min_hash_sim.sh source/folder/document
6. tf-idf

        $ ~/path/to/prima/tools/tfidf.sh filetype(.csv/.tsv)
7. Word count

        $ ~/path/to/prima/tools/word_count.sh

More information on how exactly to use these can be found in the [wiki.](https://github.com/U-Alberta/prima/wiki/Tools)
