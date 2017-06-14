#include "minHash.h"

void main() {
	int retval = minHash();
}

int minHash() {
  sqlite3* db;
  sqlite3_stmt* stmt;
	int rc=0, shingleLenSum=0;
  DocShingles* s;
  MinHash* h;

  int* hashNums = genRandom();
  rc = sqlite3_open(db_name, &db);
  if (rc) {
    fprintf(stderr, "Error opening database %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    return -1;
  }
  /*
	The results of first two SQL statements are used to malloc s and h below.
  */
  int documentCount = sqlStmtOne(rc, db, stmt);
  if (documentCount == 0) {
    return -1;
  }
  int* shingleLengths = (int*) malloc(sizeof(int)*documentCount);
  for (int i=0; i<documentCount; ++i) {
    shingleLengths[i] = 0;
  }
  shingleLengths = sqlStmtTwo(documentCount, shingleLengths, rc, db, stmt);
  if (shingleLengths[0] == 0) {
    return -1;
  }
  for (int i=0; i<documentCount; ++i) {
    shingleLenSum+=shingleLengths[i];
  }
  /*
  Initialize the sizes of s and h for the number of documents and shingles. 
  hashNums generates HASHVALUES random numbers.
  */
  s = (DocShingles*) malloc((sizeof(DocShingles)*documentCount) + \
  	(sizeof(char*)*shingleLenSum));
  h = (MinHash*) malloc((sizeof(MinHash)*documentCount) + \
  	(sizeof(int)*shingleLenSum));
  /*
	The last two SQL statements populate s and h.
  */
  s = sqlStmtThree(documentCount, s, rc, db, stmt);
  if (s[0].docid == NULL) {
    return -1;
  }
  s = sqlStmtFour(documentCount, s, rc, db, stmt);
  if (s[0].docid == NULL) {
    return -1;
  }
  sqlite3_close(db);

  /*
	Loop through shingles in every document calculating initial hash values.
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
  printToCSV saves all the documents and their corresponding minHash values to 
  a csv file in the processed/min_hash directory. Finally free all malloc'd
  memory.
  */
  printToCSV(h, documentCount);
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
The first SQL statement gets the number of documents in the collection.
*/
int sqlStmtOne(int rc, sqlite3* db, sqlite3_stmt* stmt) {
  int documentCount;
  rc = sqlite3_prepare_v2(db, sql_select_stmt_one, -1, &stmt, 0);
  if (rc != SQLITE_OK) {  
    fprintf(stderr, "Preparation failed: %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    return 0;
  }
  while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
    documentCount = atoi(sqlite3_column_text(stmt, 0));
  }
  sqlite3_finalize(stmt);
  return documentCount;
}

/*
The second SQL statement gets the number of shingles in each document 
in the collection and the sum of these shingles.
*/
int* sqlStmtTwo(int documentCount, int* shingleLengths, int rc, sqlite3* db, \
  sqlite3_stmt* stmt) {
  rc = sqlite3_prepare_v2(db, sql_select_stmt_two, -1, &stmt, 0);
  if (rc != SQLITE_OK) {  
    fprintf(stderr, "Preparation failed: %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    shingleLengths[0] = 0;
  }
  else {
    while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
      int id = atoi(sqlite3_column_text(stmt, 0));
      int length = atoi(sqlite3_column_text(stmt, 1));
      shingleLengths[id] = length;
    }
    sqlite3_finalize(stmt);
  }
  return shingleLengths;
}

/*
The third SQL statement loops through all the documents, populating 
s[i].docid with the name of that document.
*/
DocShingles* sqlStmtThree(int documentCount, DocShingles* s, int rc, sqlite3* db, sqlite3_stmt* stmt) {
  for (int i=0; i<documentCount; ++i) {
    rc = sqlite3_prepare_v2(db, sql_select_stmt_three, -1, &stmt, 0);
    sqlite3_bind_int(stmt, 1, i);
    if (rc != SQLITE_OK) {  
      fprintf(stderr, "Preparation failed: %s\n", sqlite3_errmsg(db));
      sqlite3_close(db);
      s[0].docid = NULL;
    }
    else {
      int string_lengths = 0;
      while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
        const char* txt = sqlite3_column_text(stmt, 0);
        string_lengths += strlen(txt) + 1;
        s[i].docid = (char*) malloc(sizeof(char*)+string_lengths);
        strcpy(s[i].docid, txt);
      }
      sqlite3_reset(stmt);
      sqlite3_finalize(stmt);
    }
  }
  return s;
}

/*
The fourth SQL statement loops through all the documents, populating 
s[i].shingles with the shingles in that document.
*/
DocShingles* sqlStmtFour(int documentCount, DocShingles* s, int rc, sqlite3* db, sqlite3_stmt* stmt) {
  for (int i=0; i<documentCount; ++i) {
  	rc = sqlite3_prepare_v2(db, sql_select_stmt_four, -1, &stmt, 0);
  	sqlite3_bind_int(stmt, 1, i);
		if (rc != SQLITE_OK) {  
		  fprintf(stderr, "Preparation failed: %s\n", sqlite3_errmsg(db));
		  sqlite3_close(db);
		  s[0].docid = NULL;
		}
		else {
			s[i].shingles = (char**) malloc(sizeof(char**));
			int shinglenum = 0;
			int string_lengths = 0;
			while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
				const char* txt = sqlite3_column_text(stmt, 0);
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
  }
  return s;
}

/*
This first allocates memory for every new min hash the for every document and 
every hash function. Then it finds the minimum hash value for each document and 
hash function (hashNums) pair and saves that to h[].minHashes[].
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

/*
Print a table of documents and their hash values to a csv file.
*/
void printToCSV(MinHash *h, int documentCount) {
  time_t t;
  struct tm *tm;
  time (&t);
  tm = localtime (&t);
  char* time_str;
  FILE *fp;
  char *filename = "processed/min_hash/min_hash.csv";
  fp = fopen(filename, "w+");
  fprintf(fp, "%s", asctime(tm));
  fprintf(fp, " ");
  for (int i=0; i<documentCount; ++i) {
    fprintf(fp, ", %s", h[i].docid);
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