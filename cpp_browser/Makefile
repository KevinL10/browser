EXE = browser
OBJS = browser.o request.o
WARNINGS = -pedantic -Wall -Werror -Wfatal-errors -Wextra -Wno-unused-parameter -Wno-unused-variable

CXXFLAGS = -std=c++14 -g -O0 $(WARNINGS) -MP -c 
CXX = clang++
LD = clang++
LDFLAGS = -std=c++14 -lssl


all: browser

$(EXE): $(OBJS)
	$(LD) $(OBJS) $(LDFLAGS) -o $(EXE)

browser.o: browser.cpp
	$(CXX) $(CXXFLAGS) browser.cpp -o $@

request.o: request.cpp request.h
	$(CXX) $(CXXFLAGS) request.cpp -o $@

clean:
	-rm -rf *.o $(EXE)