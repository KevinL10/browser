EXE = browser
OBJ = browser.o
CXX = g++

all: $(EXE)

$(EXE): browser.o
	$(CXX) -o browser browser.o

$(EXE).o: browser.cpp
	$(CXX) -c browser.cpp -o browser.o




clean:
	rm -rf $(EXE) $(OBJ)


.PHONY: all tidy clean