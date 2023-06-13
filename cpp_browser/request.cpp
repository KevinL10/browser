#include "request.h"

#include <bits/stdc++.h>
#include <netdb.h>
#include <netinet/in.h>
#include <openssl/ssl.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/types.h>

#include <cctype>
#include <cstring>
#include <iostream>

#include "utils.h"

#define BUFFER_SIZE 1024

using namespace std;

void HttpResponse::print() {
    for (auto &[key, value] : headers) {
        cout << "header:" << key << "=" << value << "\n";
    }
    cout << "body:\n" << body;
}

string HttpResponse::toString() {
    string out = "";
    for (auto &[key, value] : headers) {
        out += "header:" + key + "=" + value + "\n";
    }
    return out +  "body:\n" + body;
}


// Creates a socket to the given url hostname and attempts connection. Returns
// -1 on failure.
int create_socket(const URL &url) {
    int socketFd = socket(AF_INET, SOCK_STREAM, 0);
    if (socketFd == -1) {
        cerr << "Failed to create socket.\n";
        return -1;
    }

    struct hostent *server = gethostbyname(url.hostname.c_str());
    if (server == nullptr) {
        cerr << "Failed to resolve hostname.\n";
        close(socketFd);
        return -1;
    }

    // Constructs the server address structure
    struct sockaddr_in serverAddress {};
    memset(&serverAddress, 0, sizeof(serverAddress));
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(443);
    memcpy(&serverAddress.sin_addr.s_addr, server->h_addr, server->h_length);

    if (connect(socketFd, (struct sockaddr *)&serverAddress,
                sizeof(serverAddress)) < 0) {
        cerr << "Failed to connect to the server.\n";
        close(socketFd);
        return -1;
    }

    return socketFd;
}

// Returns the HTTP GET request string
string getHttpRequest(const URL &url) {
    return "GET " + url.path + " HTTP/1.1\r\n" + "Host: " + url.hostname +
           "\r\n" + "Connection: close\r\n" + "\r\n";
}

// Returns the full response headers and body for HTTP request
string sendHttpGetRequest(const URL &url) {
    int socketFd = create_socket(url);
    if (socketFd == -1) return "";

    // Send the HTTP GET request
    string request = getHttpRequest(url);
    if (send(socketFd, request.c_str(), request.size(), 0) < 0) {
        cerr << "Failed to write to socket.\n";
        close(socketFd);
        return "";
    }

    // Receive the HTTP response
    string response = "";
    char buffer[BUFFER_SIZE];
    ssize_t nbytes = 0;
    while ((nbytes = recv(socketFd, buffer, sizeof(buffer), 0)) > 0) {
        response.append(buffer, nbytes);
    }
    close(socketFd);
    return response;
}

// Returns the full response headers and body for HTTPS request
string sendHttpsGetRequest(const URL &url) {
    int socketFd = create_socket(url);
    if (socketFd == -1) return "";

    // Construct the OpenSSL ctx and connection
    SSL_CTX *ctx = SSL_CTX_new(TLS_client_method());
    if (ctx == nullptr) {
        cerr << "Failed to create SSL_CTX object.\n";
        close(socketFd);
        return "";
    }

    SSL *ssl = SSL_new(ctx);
    if (ssl == nullptr) {
        cerr << "Failed to create SSL connection.\n";
        SSL_CTX_free(ctx);
        close(socketFd);
        return "";
    }

    if (SSL_set_fd(ssl, socketFd) <= 0) {
        cerr << "Failed to attach SSL to socket.\n";
        SSL_free(ssl);
        SSL_CTX_free(ctx);
        close(socketFd);
        return "";
    }

    // Perform the SSL handshake
    if (SSL_connect(ssl) != 1) {
        cerr << "Failed to perform SSL handshake" << std::endl;
        SSL_shutdown(ssl);
        SSL_free(ssl);
        SSL_CTX_free(ctx);
        close(socketFd);
        return "";
    }

    // Send the HTTP GET request
    string request = getHttpRequest(url);
    if (SSL_write(ssl, request.c_str(), request.size()) < 0) {
        cerr << "Failed to write to socket.\n";
        SSL_shutdown(ssl);
        SSL_free(ssl);
        SSL_CTX_free(ctx);
        close(socketFd);
        return "";
    }

    // Receive the HTTP response
    string response = "";
    char buffer[BUFFER_SIZE];
    ssize_t nbytes = 0;
    while ((nbytes = SSL_read(ssl, buffer, sizeof(buffer))) > 0) {
        response.append(buffer, nbytes);
    }

    SSL_shutdown(ssl);
    SSL_free(ssl);
    SSL_CTX_free(ctx);
    close(socketFd);
    return response;
}

// Parses the given URL into a structured object
URL parseUrl(string url) {
    URL output;

    vector<string> schemes = {"https", "http"};
    for (string scheme : schemes) {
        if (url.substr(0, scheme.length()) == scheme) {
            output.scheme = scheme;
            url = url.substr(scheme.length() + 3);
        }
    }

    size_t slashIndex = url.find("/");
    if (slashIndex == string::npos) {
        output.hostname = url.substr(0, slashIndex);
        output.path = "/";
    } else {
        output.hostname = url.substr(0, slashIndex);
        output.path = url.substr(slashIndex);
    }
    return output;
}

// Returns a structured HttpResponse object from the raw HTTP response
HttpResponse extractHeadersAndBody(string response) {
    // replaceAll(response, "\r\n", "\n");

    HttpResponse httpResponse;
    stringstream ss(response);

    string version, status, explanation;
    ss >> version >> status >> explanation;
    if (status != "200") {
        cerr << status << " " << explanation << "\n";
        return httpResponse;
    }
    // ignore the \r\n after the first line
    ss.ignore();
    ss.ignore();

    string headerLine;
    while (getline(ss, headerLine, '\n')) {
        if (headerLine == "\r") {
            break;
        }

        size_t colonIndex = headerLine.find(":");
        string header = headerLine.substr(0, colonIndex);
        string value = headerLine.substr(colonIndex + 1);

        // lowercase header and strip value
        transform(header.begin(), header.end(), header.begin(),
                  [](unsigned char c) { return tolower(c); });
        httpResponse.headers[header] = trim(value);
    }

    httpResponse.body = ss.str().substr(ss.tellg());
    return httpResponse;
}

HttpResponse sendGetRequest(string url) {
    URL structuredUrl = parseUrl(url);
    string response = sendHttpsGetRequest(structuredUrl);
    HttpResponse httpResponse = extractHeadersAndBody(response);
    return httpResponse;
}