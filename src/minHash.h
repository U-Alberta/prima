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
  char* docid;
  char** shingles;
  int* hash;
}DocShingles;

/*
For each document save the corresponding unique id (from DocShingles) and for 
each of the HASHVALUES hash functions save the smallest hash value.
*/
typedef struct {
  char* docid;
  int* minHashes;
} MinHash;

char* db_name = "processed/shingles.db";
char* sql_select_stmt_one = "SELECT COUNT(*) FROM Document;";
char* sql_select_stmt_two = "SELECT docid, COUNT(*) FROM Shingle GROUP BY docid;";
char* sql_select_stmt_three = "SELECT DISTINCT docname FROM Document WHERE docid=?";
char* sql_select_stmt_four = "SELECT shingle FROM Shingle WHERE docid=?;";

void main();
void callMinHash();
int minHash();
int sqlStmtOne(int rc, sqlite3* db, sqlite3_stmt* stmt);
int* sqlStmtTwo(int documentCount, int* shingleLengths, int rc, sqlite3* db, sqlite3_stmt* stmt);
DocShingles* sqlStmtThree(int documentCount, DocShingles* s, int rc, sqlite3* db, sqlite3_stmt* stmt);
DocShingles* sqlStmtFour(int documentCount, DocShingles* s, int rc, sqlite3* db, sqlite3_stmt* stmt);
int* genRandom();
MinHash* getMinHash(DocShingles* s, MinHash* h, int* hashNums, int* shingleLengths, int documentCount);
int hash(unsigned char* str);
void printToCSV(MinHash *h, int documentCount);
void freeEverything(int* hashNums, DocShingles* s, MinHash* h, int* shingleLengths, int documentCount);