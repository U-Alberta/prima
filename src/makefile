all: makeminhash makemodule

makeminhash: minHash.c sqlite3.c
	gcc -o minHash minHash.c sqlite3.c -lpthread -ldl

makemodule: minHashModule.c sqlite3.c
	gcc -shared -fPIC -I/usr/include/python2.7/ -lpython2.7 -o minHash.so minHashModule.c sqlite3.c -lpthread -ldl

clean:
	rm -f minHash minHash.so