#include "request.h"

using namespace std;

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