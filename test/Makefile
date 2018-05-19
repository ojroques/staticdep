CC    = gcc
FLAGS = -Wall -Wextra -pedantic
EXE   = file1 file11 file12 file111 file1X2
OBJ   = file1.o file11.o file12.o file111.o file1X2.o

.PHONY = exe obj clean ultraclean

exe: $(EXE)

obj: $(OBJ)

#################### FILE1 ####################
file1: file1.o
	$(CC) $(FLAGS) $^ -o $@

file1.o: file1.c file1.h
	$(CC) $(FLAGS) -c $< -o $@

#################### FILE11 ###################
file11: file11.o file1.o
	$(CC) $(FLAGS) $^ -o $@

file11.o: file11.c file11.h file1.h
	$(CC) $(FLAGS) -c $< -o $@

#################### FILE12 ###################
file12: file12.o file1.o
	$(CC) $(FLAGS) $^ -o $@

file12.o: file12.c file12.h file1.h
	$(CC) $(FLAGS) -c $< -o $@

#################### FILE111 ##################
file111: file111.o file11.o file1.o
	$(CC) $(FLAGS) $^ -o $@

file111.o: file111.c file111.h file11.h file1.h
	$(CC) $(FLAGS) -c $< -o $@

#################### FILE1X2 ##################
file1X2: file1X2.o file11.o file12.o file1.o
	$(CC) $(FLAGS) $^ -o $@

file1X2.o: file1X2.c file1X2.h file11.h file12.h file1.h
	$(CC) $(FLAGS) -c $< -o $@

#################### OTHERS ###################
clean:
	rm -f $(OBJ) 

ultraclean:
	rm -f $(OBJ) $(EXE)
