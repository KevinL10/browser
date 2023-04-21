from browser.main import *


def test_request_file_url():
    headers, body = request("data:text/html,Hello world!")
    assert body == "Hello world!"


def test_request_http_url():
    for url in ["http://example.org", "http://example.org/"]:
        headers, body = request(url)
        assert "Example Domain" in body


def test_request_https_url():
    for url in ["https://example.org", "https://example.org/"]:
        headers, body = request(url)
        assert "Example Domain" in body


def test_show_entities():
    assert show("<body>aaa&lt;div&gt;bbb</body>") == "aaa<div>bbb"


def test_show_body():
    assert show("abcd<body>123</body>efgh") == "123"
