#include "browser.h"

#include <bits/stdc++.h>
#include <netdb.h>
#include <netinet/in.h>
#include <openssl/ssl.h>
#include <stdio.h>
#include <sys/ioctl.h>
#include <sys/socket.h>
#include <sys/types.h>

#include <cstring>
#include <iostream>

#define BUFFER_SIZE 1024

using namespace std;

// Returns the full response headers and body
string sendHttpGetRequest(const string &host, const string &path) {
    int socketFd = socket(AF_INET, SOCK_STREAM, 0);
    if (socketFd == -1) {
        cerr << "Failed to create socket.\n";
        return "";
    }

    struct hostent *server = gethostbyname(host.c_str());
    if (server == nullptr) {
        cerr << "Failed to resolve hostname.\n";
        close(socketFd);
        return "";
    }

    // Constructs the server address structure
    struct sockaddr_in serverAddress {};
    memset(&serverAddress, 0, sizeof(serverAddress));
    serverAddress.sin_family = AF_INET;
    serverAddress.sin_port = htons(80);
    memcpy(&serverAddress.sin_addr.s_addr, server->h_addr, server->h_length);

    if (connect(socketFd, (struct sockaddr *)&serverAddress,
                sizeof(serverAddress)) < 0) {
        cerr << "Failed to connect to the server.\n";
        close(socketFd);
        return "";
    }

    // Send the HTTP GET request
    string request = "GET " + path + " HTTP/1.1\r\n" + "Host: " + host +
                     "\r\n" + "Connection: close\r\n" + "\r\n";
    if (send(socketFd, request.c_str(), request.size(), 0) < 0) {
        cerr << "Failed to write to socket.\n";
        close(socketFd);
        return "";
    }

    string response = "";
    char buffer[1];
    ssize_t nbytes = 0;
    while ((nbytes = recv(socketFd, buffer, sizeof(buffer), 0)) > 0) {
        response.append(buffer, nbytes);
    }
    close(socketFd);
    return response;
}

// Returns the full response headers and body
string sendHttpsGetRequest(const URL &url) {
    int socketFd = socket(AF_INET, SOCK_STREAM, 0);
    if (socketFd == -1) {
        cerr << "Failed to create socket.\n";
        return "";
    }

    struct hostent *server = gethostbyname(url.hostname.c_str());
    if (server == nullptr) {
        cerr << "Failed to resolve hostname.\n";
        close(socketFd);
        return "";
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
        return "";
    }

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
    string request = "GET " + url.path + " HTTP/1.1\r\n" +
                     "Host: " + url.hostname + "\r\n" +
                     "Connection: close\r\n" + "\r\n";
    if (SSL_write(ssl, request.c_str(), request.size()) < 0) {
        cerr << "Failed to write to socket.\n";
        SSL_shutdown(ssl);
        SSL_free(ssl);
        SSL_CTX_free(ctx);
        close(socketFd);
        return "";
    }

    string response = "";
    char buffer[1];
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

int main(int argc, char **argv) {
    if (argc > 2) {
        cout << "Usage: ./browser <url>\n";
        return 0;
    }

    string url = (argc == 1) ? "https://example.org" : argv[1];

    URL structuredUrl = parseUrl(url);
    cout << structuredUrl.hostname << " " << structuredUrl.path << " "
         << structuredUrl.scheme << "\n";
    string response = sendHttpsGetRequest(structuredUrl);

    cout << response << "\n";
}