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
    string toString();
};

HttpResponse sendGetRequest(string url);

const string HTTPX_PREFIX = "http";
const string FILE_PREFIX = "file";
#endif