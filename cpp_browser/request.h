#ifndef REQUESTS_H
#define REQUESTS_H

#include <iostream>
#include <map>

using namespace std;

struct URL {
    string scheme;
    string hostname;
    string path;
    int port;
};

struct HttpResponse {
    map<string, string> headers;
    string body;

    void print(); 
};

HttpResponse sendGetRequest(string url);

#endif