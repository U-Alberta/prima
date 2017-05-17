/* Write a C program, in a file called q9.c that takes an airport IATA code as 
a parameter and produces the equivalent answer of question 8 above for that 
airport.*/

#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include "sqlite3.h"

#define ARRAY_SIZE 1024

/*The string.h and stdlib.h libraries are used to save the results of a query 
into a data structure in C.*/

int main (int argc, char **argv) {
  sqlite3 *db;
  sqlite3_stmt *stmt;
  int rc;
  int col;

/*First open the database used as the second command line argument or return 
an error if it can't be opened.*/
  if (argc != 3) {
    fprintf(stderr, "Usage: %s <database file> <airport IATA>\n", argv[0]);
    return(1);
  }
  rc = sqlite3_open(argv[1], &db);
  if (rc) {
    fprintf(stderr, "Can't open database: %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    return(1);
  }

/* Much like q8.c, this query is a combination of a recursive query which 
selects all airports reachable flying from the input IATA and the selection of 
all airports with commercial airlines flying into or out of them. 
The only difference between this an q8.c is the use of Cs malloc function to 
include the given IATA code in the query..*/
  char *sql_recursive_select_stmt = malloc(sizeof(char *) * ARRAY_SIZE);
  strcpy(sql_recursive_select_stmt,
    "WITH RECURSIVE YEG_Routes(Source_airport, Destination_airport) AS " \
    "(SELECT Source_airport, Destination_airport FROM Routes " \
    "UNION " \
    "SELECT routes.Source_airport, edmonton.Destination_airport " \
    "FROM YEG_Routes edmonton, Routes routes " \
    "WHERE edmonton.Source_airport=routes.Destination_airport) " \
    "SELECT DISTINCT Source_Airport " \
    "FROM Routes route " \
    "INNER JOIN Commercial_Airlines airline " \
    "ON airline.Airline_ID=route.Airline_ID " \
    "UNION " \
    "SELECT DISTINCT Destination_airport " \
    "FROM Routes route " \
    "INNER JOIN Commercial_Airlines airline " \
    "ON airline.Airline_ID=route.Airline_ID " \
    "EXCEPT " \
    "SELECT Destination_airport " \
    "FROM YEG_Routes " \
    "WHERE Source_airport='");
  sprintf(sql_recursive_select_stmt + strlen(sql_recursive_select_stmt), "%s", argv[2]);
  sprintf(sql_recursive_select_stmt + strlen(sql_recursive_select_stmt), "';");

  rc = sqlite3_prepare_v2(db, sql_recursive_select_stmt, -1, &stmt, 0);
  if (rc != SQLITE_OK) {  
    fprintf(stderr, "Preparation failed: %s\n", sqlite3_errmsg(db));
    sqlite3_close(db);
    return 1;
  }
  while ((rc = sqlite3_step(stmt)) == SQLITE_ROW) {
    for (col = 0; col < sqlite3_column_count(stmt) - 1; col++) {
      printf("%s|", sqlite3_column_text(stmt, col));
    }
    printf("%s", sqlite3_column_text(stmt, col));
    printf("\n");
  }
  sqlite3_finalize(stmt);
  free(sql_recursive_select_stmt);
}