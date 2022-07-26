CC=g++
CFLAGS = -g -c -Wall -pedantic -std=c++14

default: 
	$(CC) -o main main.o

%.o:
	$(CC) $(CFLAGS) $*.cpp

clean:
	rm *.o
	rm main