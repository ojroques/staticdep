CC    = gcc
FLAGS = -Wall -Wextra -pedantic
EXEC  = sdep

.PHONY = all clean ultraclean

all: $(EXEC)

sdep: sdep.c sdep.h
	$(CC) $(FLAGS) $< -o $@

clean:
	rm -f *.o

ultraclean:
	rm -f *.o $(EXEC)
