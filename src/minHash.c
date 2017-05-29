#include "minhash.h"

void main() {
	int retval = minHash();
}

int minHash() {
  sqlite3* db;
  sqlite3_stmt* stmt;
	int rc=0, col=0, documentCount=0;
  int* shingleLengths;
  DocShingles* s;
  MinHash* h;

  /*
  The first SQL statement gets the number of documents in the collection.
  */
  rc = sqlite3_open(db_name, &db);
  if (rc) {
    fprintf(stderr, "Can't open database %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    return 1;
  }
  rc = sqlite3_prepare_v2(db, sql_select_stmt_one, -1, &stmt, 0);
  if (rc != SQLITE_OK) {  
    fprintf(stderr, "Preparation failed: %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    return 1;
  }
  while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
	  documentCount = atoi(sqlite3_column_text(stmt, 0));
	}
  sqlite3_finalize(stmt);

  /*
  The second SQL statement gets the number of shingles in each document 
  in the collection and the sum of these shingles.
  */
  shingleLengths = (int*) malloc(sizeof(int)*documentCount);
  rc = sqlite3_prepare_v2(db, sql_select_stmt_two, -1, &stmt, 0);
  if (rc != SQLITE_OK) {  
    fprintf(stderr, "Preparation failed: %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    return 1;
  }
  int shingleLenSum = 0;
  while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
  	int id = atoi(sqlite3_column_text(stmt, 0));
  	int length = atoi(sqlite3_column_text(stmt, 1));
  	shingleLengths[id] = length;
  	shingleLenSum += length;
  }
  sqlite3_finalize(stmt);

  /*
  Initialize the sizes of s and h for the number of documents and shingles. 
  hashNums generates HASHVALUES random numbers.
  */
  s = (DocShingles*) malloc((sizeof(DocShingles)*documentCount) + \
  	(sizeof(char*)*shingleLenSum));
  h = (MinHash*) malloc((sizeof(MinHash)*documentCount) + \
  	(sizeof(int)*shingleLenSum));
  int* hashNums = genRandom();

  /*
	The third SQL statement loops through all the documents, populating 
	s[i].shingles with the shingles in that document.
  */
  for (int i=0; i<documentCount; ++i) {
  	rc = sqlite3_prepare_v2(db, sql_select_stmt_three, -1, &stmt, 0);
  	sqlite3_bind_int(stmt, 1, i);
		if (rc != SQLITE_OK) {  
		  fprintf(stderr, "Preparation failed: %s\n", sqlite3_errmsg(db));
		  sqlite3_close(db);
		  return 1;
		}
		s[i].shingles = (char**) malloc(sizeof(char**));
		s[i].docid = i;
		int shinglenum = 0;
		int string_lengths = 0;
		while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
			const char* txt = sqlite3_column_text(stmt, 1);
			string_lengths += strlen(txt) + 1;
			s[i].shingles = (char**) realloc(s[i].shingles, sizeof(char**)+\
				string_lengths);
			s[i].shingles[shinglenum] = (char*) malloc(strlen(txt)+1);
			strcpy(s[i].shingles[shinglenum], txt);
			++shinglenum;
		}
		sqlite3_reset(stmt);
		sqlite3_finalize(stmt);
  }
  sqlite3_close(db);

  /*
	Then loop through shingles in every document calculating initial hash values.
  */
  for (int i=0; i<documentCount; ++i) {
    s[i].hash = (int*) malloc(sizeof(int*) * shingleLengths[i]);
    for (int j=0; j<shingleLengths[i]; ++j) {
      s[i].hash[j] = hash(s[i].shingles[j]);
    }
  }

  /*
	getMinHash calculates the new hash values and saves the minimum of each hash 
	value for each function and document.
  */
  h = getMinHash(s, h, hashNums, shingleLengths, documentCount);
  /*
  Just for printing values.
  */
  /*for (int i=0; i<documentCount; ++i) {
    printf("%i\n", h[i].docid);
    for (int j=0; j<HASHVALUES; ++j) {
      printf("%i\n", h[i].minHashes[j]);
    }
  }*/
  /*
  TODO: output to a csv file (sqlite3 db would be so much nicer tbh)
  */
  print_to_csv(h, documentCount);

  freeEverything(hashNums, s, h, shingleLengths, documentCount);
  return 1;
}

/*
Generate HASHVALUES random numbers to be used as hash functions later.
*/
int* genRandom() {
  int* hashNums = malloc(sizeof(int)*HASHVALUES);
  for (int i=0; i<HASHVALUES; ++i) {
    int r = rand();
    hashNums[i] = r;
  }
  return hashNums;
}

/*
This first allocates memory for every new min hash the for every document and 
every hash function, finds the minimum hash value and saves that to h.
*/
MinHash* getMinHash(DocShingles* s, MinHash* h, int* hashNums, \
	int* shingleLengths, int documentCount) {
  for (int i=0; i<documentCount; ++i) {
    h[i].minHashes = (int*) malloc(sizeof(int*) * HASHVALUES);
  }
  for (int i=0; i<documentCount; ++i) {
    h[i].docid = s[i].docid;
    for (int j=0; j<HASHVALUES; ++j) {
      int hashFunc = hashNums[j];
      double minHashj = INFINITY;
      for (int k=0; k<shingleLengths[i]; ++k) {
        int hash1 = s[i].hash[k];
        int hashj = hash1 ^ hashFunc;
        if (hashj < minHashj) {
          minHashj = hashj;
        }
      }
      h[i].minHashes[j] = minHashj;
    }
  }
  return h;
}

/*
I implemented the first hash function on this page: 
http://www.cse.yorku.ca/~oz/hash.html
and on my (tiny) sample there were no collisions on disjoint shingles which is 
cool.
TODO: Find a better hash function.
*/
int hash(unsigned char* str) {
  unsigned long hash = 5381;
  int c;
  while (c = *str++)
    hash = ((hash << 5) + hash) + c; /* hash * 33 + c */
  return hash;
}

void print_to_csv(MinHash *h, int documentCount) {
  FILE *fp;
  char *filename = "processed/min_hash/min_hash.csv";
  fp = fopen(filename, "w+");
  fprintf(fp, " ");
  for (int i=1; i<=documentCount; ++i) {
    fprintf(fp, ", %i", i);
  }
  for (int i=0; i<HASHVALUES; ++i) {
    fprintf(fp, "\n%i", i+1);
    for (int j=0; j<documentCount; ++j) {
      fprintf(fp, ", %i", h[j].minHashes[i]);
    }
  }
  fclose(fp);
}

/*
Free all malloc'd memory.
*/
void freeEverything(int* hashNums, DocShingles* s, MinHash* h, int* shingleLengths, int documentCount) {
  for (int i=0; i<documentCount; ++i) {
  	free(h[i].minHashes);
  	free(s[i].hash);
    for (int j=0; j<shingleLengths[i]; ++j) {
      free(s[i].shingles[j]);
    }
    free(s[i].shingles);
  }
  free(hashNums);
  free(h);
  free(s);
  free(shingleLengths);
}