from browser.main import *

def test_parse_file_url():
    headers, body = request("data:text/html,Hello world!")
    assert body == "Hello world!"

def test_parse_http_url():
    for url in ["http://example.org", "http://example.org/"]:
        headers, body = request(url)
        assert "Example Domain" in body


def test_parse_https_url():
    for url in ["https://example.org", "https://example.org/"]:
        headers, body = request(url)
        assert "Example Domain" in body
