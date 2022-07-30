CC=g++
CFLAGS= -g -c -Wall -pedantic -std=c++14
LFLAGS= -lcurl

default: main.o
	$(CC) -o main main.o ${LFLAGS}

%.o: %.cpp 
	$(CC) $(CFLAGS) $*.cpp

clean: 
	rm *.o
	rm main