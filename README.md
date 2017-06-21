# prima
Personal Research Management for the IA

## Installation
1. Clone this repository to somewhere in your file system.
2. To install the tool, first [download SQLite](https://sqlite.org/download.html) and place the files titled sqlite3.c and sqlite3.h in the prima/src directory. Then run

        $ sudo python setup.py install
3. To create the appropriate directories for your file system run the following commands where **project_name** is the desired file name for a collection to be saved in

        $ init_workspace.sh
        $ cd workspace
        $ init_project.sh project_name
        $ cd project_name
        $ init_collection.sh
4. To download a collection into the auto-generated source/ directory, run the following where **collection_name** is a valid id for a collection in archive.org (for example [this](https://archive.org/details/toronto) collection would use collection_name=toronto)

        $ fetch_collection.sh collection_name 

5. After completing steps 1-5, run the following to get stats on your collection where **tool** is one of the options listed below with the appropriate parameters

        $ toolname params
6. For every new collection to be created, make sure you're in the workspace directory and repeat step 3 lines 3-5 and step 4 with the new collection name before using any tools.

## Tools
Current available tools included in the prima and basic examples are:
1. BM25 (default k=10)

        $ bm25.sh [k] "sample query here"
2. K-means clustering (default k=3)

        $ k_means_clusterer.sh [k]
3. Latent Dirichlet allocation (default k=100)

        $ lda.sh [k]
4. Latent semantic indexing (default k=100)

        $ lsi.sh [k]
5. MinHash (default k=10)

        $ min_hash.sh
        $ min_hash_sim.sh source/folder/document [k]
6. tf-idf

        $ tfidf.sh
7. Word count

        $ word_count.sh

More detail on how exactly to use these can be found in the [wiki.](https://github.com/U-Alberta/prima/wiki/Tools)
