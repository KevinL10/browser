EXE = browser
OBJS = browser.o request.o utils.o
WARNINGS = -pedantic -Wall -Werror -Wfatal-errors -Wextra -Wno-unused-parameter -Wno-unused-variable

CXXFLAGS = -std=c++17 -g -O0 $(WARNINGS) -MP -c  $(shell pkg-config --cflags gtkmm-4.0)
CXX = clang++
LD = clang++
LDFLAGS = -std=c++17 -lssl $(shell pkg-config --libs gtkmm-4.0)


all: browser

$(EXE): $(OBJS)
	$(LD) $(OBJS) $(LDFLAGS) -o $(EXE)

browser.o: browser.cpp
	$(CXX) $(CXXFLAGS) browser.cpp -o $@

request.o: request.cpp request.h
	$(CXX) $(CXXFLAGS) request.cpp -o $@

utils.o: utils.cpp utils.h
	$(CXX) $(CXXFLAGS) utils.cpp -o $@

clean:
	-rm -rf *.o $(EXE)