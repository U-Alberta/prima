#include "minHash.h"

int main() {
    printf("main function\n");
    return 1;
}

static char minHash_docstring[] = "A quick minimum hashing function.";

static PyMethodDef module_methods[] = {
    {"minHash", minHash_minHash, METH_VARARGS, minHash_docstring},
    {NULL, NULL, 0, NULL}
};

void init_minHash(void) {
    Py_InitModule3("_minHash", module_methods, minHash_docstring);
}

static PyObject *minHash_minHash(PyObject *self, PyObject *args) {
    sqlite3 *db;
    sqlite3_stmt *stmt;
    int rc=0, shingleLenSum=0, hashvalues=0;
    DocShingles *s;
    MinHash *h;

    if (!PyArg_ParseTuple(args, "i", &hashvalues))
        return NULL;

    int *hashNums = genRandom(hashvalues);
    rc = sqlite3_open(db_name, &db);
    if (rc) {
        fprintf(stderr, "Error opening database %s\n", sqlite3_errmsg(db));
        sqlite3_close(db);
        Py_RETURN_NONE;
    }
    /*
    The results of first two SQL statements are used to malloc s and h below.
    */
    int documentCount = sqlStmtOne(rc, db, stmt);
    if (documentCount == 0) {
        Py_RETURN_NONE;
    }
    int *shingleLengths = (int*) malloc(sizeof(int)*documentCount);
    for (int i=0; i<documentCount; ++i) {
        shingleLengths[i] = 0;
    }
    shingleLengths = sqlStmtTwo(documentCount, shingleLengths, rc, db, stmt);
    if (shingleLengths[0] == 0) {
        Py_RETURN_NONE;
    }
    for (int i=0; i<documentCount; ++i) {
        shingleLenSum+=shingleLengths[i];
    }
    /*
    Initialize the sizes of s and h for the number of documents and shingles. 
    hashNums generates hashvalues random numbers.
    */
    s = (DocShingles*) malloc((sizeof(DocShingles)*documentCount)\
        +(sizeof(char*)*shingleLenSum));
    h = (MinHash*) malloc((sizeof(MinHash)*documentCount)\
        +(sizeof(int)*shingleLenSum));
    /*
    The last two SQL statements populate s and h.
    */
    s = sqlStmtThree(documentCount, s, rc, db, stmt);
    if (s[0].docid == NULL) {
        Py_RETURN_NONE;
    }
    s = sqlStmtFour(documentCount, s, rc, db, stmt);
    if (s[0].docid == NULL) {
        Py_RETURN_NONE;
    }
    sqlite3_close(db);

    /*
    Loop through shingles in every document calculating initial hash values.
    */
    for (int i=0; i<documentCount; ++i) {
        s[i].hash = (int*) malloc(sizeof(int*)  *shingleLengths[i]);
        for (int j=0; j<shingleLengths[i]; ++j) {
            s[i].hash[j] = hash(s[i].shingles[j]);
        }
    }

    /*
    getMinHash calculates the new hash values and saves the minimum of each hash 
    value for each function and document.
    */
    h = getMinHash(s, h, hashNums, shingleLengths, documentCount, hashvalues);

    /*
    printToCSV saves all the documents and their corresponding minHash values to 
    a csv file in the processed/min_hash directory. Finally free all malloc'd
    memory.
    */
    printToCSV(h, documentCount, hashvalues);
    freeEverything(hashNums, s, h, shingleLengths, documentCount);
    Py_RETURN_NONE;
}

/*
Generate hashvalues random numbers to be used as hash functions later.
*/
int *genRandom(int hashvalues) {
    int *hashNums = malloc(sizeof(int)*hashvalues);
    for (int i=0; i<hashvalues; ++i) {
    int r = rand();
        hashNums[i] = r;
    }
    return hashNums;
}

/*
The first SQL statement gets the number of documents in the collection.
*/
int sqlStmtOne(int rc, sqlite3 *db, sqlite3_stmt *stmt) {
    int documentCount = 0;
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
int *sqlStmtTwo(int documentCount, int *shingleLengths, int rc, sqlite3 *db, \
    sqlite3_stmt *stmt) {
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
DocShingles *sqlStmtThree(int documentCount, DocShingles *s, int rc, sqlite3 *db, sqlite3_stmt *stmt) {
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
                const char *txt = sqlite3_column_text(stmt, 0);
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
DocShingles *sqlStmtFour(int documentCount, DocShingles *s, int rc, sqlite3 *db, sqlite3_stmt *stmt) {
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
                const char *txt = sqlite3_column_text(stmt, 0);
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
MinHash *getMinHash(DocShingles *s, MinHash *h, int *hashNums, \
    int *shingleLengths, int documentCount, int hashvalues) {
    for (int i=0; i<documentCount; ++i) {
        h[i].minHashes = (int*) malloc(sizeof(int*)  *hashvalues);
    }
    for (int i=0; i<documentCount; ++i) {
        h[i].docid = s[i].docid;
        for (int j=0; j<hashvalues; ++j) {
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
int hash(unsigned char *str) {
    unsigned long hash = 5381;
    int c;
    while (c = *str++)
        hash = ((hash << 5) + hash) + c; /* hash  *33 + c */
    return hash;
}

/*
Print a table of documents and their hash values to a csv file.
*/
void printToCSV(MinHash *h, int documentCount, int hashvalues) {
    time_t t;
    struct tm *tm;
    time (&t);
    tm = localtime (&t);
    FILE *fp;
    char *filename = "processed/min_hash/min_hash.csv";
    fp = fopen(filename, "w+");
    fprintf(fp, "%s", asctime(tm));
    fprintf(fp, " ");
    for (int i=0; i<documentCount; ++i) {
        fprintf(fp, ", %s", h[i].docid);
    }
    for (int i=0; i<hashvalues; ++i) {
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
void freeEverything(int *hashNums, DocShingles *s, MinHash *h, int *shingleLengths, int documentCount) {
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