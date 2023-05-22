#include <bits/stdc++.h>
#include <netdb.h>
#include <netinet/in.h>
#include <stdio.h>
#include <sys/socket.h>
#include <sys/types.h>

#include <cstring>
#include <iostream>

using namespace std;

void parseUrl(string url) {
    const string START_PREFIX = "http://";
    if (url.substr(0, START_PREFIX.length()) != START_PREFIX) {
        cout << "Invalid URL";
        return;
    }
    url = url.substr(START_PREFIX.length());

    // split the url into host and path
    int slashIndex = url.find("/");
    string host = url.substr(0, slashIndex);
    string path = url.substr(slashIndex);

    cout << host << " " << path << "\n";

    // borrowed from https://www.linuxhowtos.org/data/6/client.c
    int sockfd, portno = 80;
    struct sockaddr_in serv_addr;
    struct hostent *server;

    server = gethostbyname(host.c_str());
    if (server == NULL) {
        perror("Error getting host");
    }

    bzero((char *)&serv_addr, sizeof(serv_addr));
    serv_addr.sin_family = AF_INET;
    serv_addr.sin_port = htons(portno);
    bcopy((char *)server->h_addr, (char *)&serv_addr.sin_addr.s_addr,
          server->h_length);

    if ((sockfd = socket(AF_INET, SOCK_STREAM, IPPROTO_TCP)) == -1) {
        perror("Error creating socket");
        return;
    }

    printf("Created socket\n");

    if (connect(sockfd, (struct sockaddr *)&serv_addr, sizeof(serv_addr)) ==
        -1) {
        close(sockfd);
        perror("Error connecting to server");
        return;
    }
    printf("Connected to server\n");

    char buffer[4096];
    string target = "GET " + path + " HTTP/1.1\r\nHost: " + host + "\r\n\r\n";
    for (int i = 0; i < target.size(); i++) {
        buffer[i] = target[i];
    }

    printf("Sending %s\n", buffer);

    int n = write(sockfd, buffer, strlen(buffer));
    read(sockfd, buffer, 4096);
    printf("%s\n", buffer);
}

int main() { parseUrl("http://example.org/index.html"); }