#include <math.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include "sqlite3.h"

#define ARRAY_SIZE 128
/* This will probably be something like 200 */
#define HASHVALUES 10

/*
For each document save a unique id, all the shingles, and all the initial hash 
values for each shingle.
*/
typedef struct {
  int docid;
  char** shingles;
  int* hash;
}DocShingles;

/*
For each document save the corresponding unique id (from DocShingles) and for 
each of the HASHVALUES hash functions save the smallest hash value.
*/
typedef struct {
  int docid;
  int* minHashes;
} MinHash;

char* db_name = "processed/shingles.db";
char* sql_select_stmt_one = "SELECT COUNT(DISTINCT docid) FROM Shingle;";
char* sql_select_stmt_two = "SELECT docid, COUNT(*) FROM Shingle GROUP BY docid;";
char* sql_select_stmt_three = "SELECT docname, shingle FROM Shingle WHERE docid=?;";

void main();
void callMinHash();
int minHash();
int* genRandom();
MinHash* getMinHash(DocShingles* s, MinHash* h, int* hashNums, int* shingleLengths, int documentCount);
int hash(unsigned char* str);
void print_to_csv(MinHash *h, int documentCount);
void freeEverything(int* hashNums, DocShingles* s, MinHash* h, int* shingleLengths, int documentCount);