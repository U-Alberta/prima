# Old makefile

all: makeminhash

makeminhash: minHashModule.c sqlite3.c
	gcc -I/usr/include/python2.7/ -lpython2.7 -o minHash minHashModule.c sqlite3.c -lpthread -ldl

clean:
	rm -f minHash