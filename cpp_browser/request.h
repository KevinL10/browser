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
};

HttpResponse sendGetRequest(string url);


// should be private; testing for now
URL parseUrl(string url);
string sendHttpGetRequest(const URL &url);
string sendHttpsGetRequest(const URL &url);
#endif