#include "minHash.c"

void callMinHash() {
	int retval = minHash();
	if (retval == -1) {
		fprintf(stderr, "Error running MinHash algorithm\n");
	}
}