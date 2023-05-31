#include "request.h"

using namespace std;

int main(int argc, char **argv) {
    if (argc > 2) {
        cout << "Usage: ./browser <url>\n";
        return 0;
    }

    string url = (argc == 1) ? "https://example.org" : argv[1];
    HttpResponse httpResponse = sendGetRequest(url);

    httpResponse.print();
}