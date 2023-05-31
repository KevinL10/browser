EXE = browser
OBJS = browser.o
WARNINGS = -pedantic -Wall -Werror -Wfatal-errors -Wextra -Wno-unused-parameter -Wno-unused-variable

CXXFLAGS = -std=c++14 -g -O0 $(WARNINGS) -MP -c 
CXX = clang++
LD = clang++
LDFLAGS = -std=c++14 -lssl


all: browser

$(EXE): $(OBJS)
	$(LD) $(OBJS) $(LDFLAGS) -o $(EXE)

browser.o: browser.cpp  browser.h
	$(CXX) $(CXXFLAGS) browser.cpp -o $@

clean:
	-rm -rf *.o $(EXE)