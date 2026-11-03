# Compilation avec :
CC= /bin/g++
CFLAGS= -Wall -Wextra -std=c++20 -fdiagnostics-color=always

# Bibliothèque standard
LIBRAIRIES_I1= -I /usr/include/c++/15

# Bibliotèque winmm, pour les sons MP3
# LIBRAIRIES_l= -lwinmm

# Paramètres de compilation
LIBRAIRIES= $(LIBRAIRIES_I1)
# OBJS= 
executable= bin/main

# Règles :
all: ${executable}

objets/%.o: sources/%.cpp
	$(CC) $(CFLAGS) -c -g $< -o $@ $(LIBRAIRIES) -lm

objets/main.o: sources/main.cpp
	$(CC) $(CFLAGS) -c -g $< -o $@ $(LIBRAIRIES) -lm

${executable}: objets/main.o
	$(CC) $(CFLAGS) -g -o $@ $^ $(LIBRAIRIES) -lm

clean:
	rm -v objets/*.o
