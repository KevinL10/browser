from browser.main import request, show
from unittest.mock import patch

def test_request_file_url():
    _, body = request("data:text/html,Hello world!")
    assert body == "Hello world!"


def test_request_http_url():
    for url in ["http://example.org", "http://example.org/"]:
        _, body = request(url)
        assert "Example Domain" in body


def test_request_https_url():
    for url in ["https://example.org", "https://example.org/"]:
        _, body = request(url)
        assert "Example Domain" in body

def test_request_view_source():
    headers, body = request("view-source:http://example.org")
    assert body.startswith('&lt;!doctype html&gt;')
    
@patch('builtins.print')
def test_show_entities(mock_print):
    
    show("<body>aaa&lt;div&gt;bbb</body>")
    mock_print.assert_called_with("aaa<div>bbb")

@patch('builtins.print')
def test_show_body(mock_print):
    show("abcd<body>123</body>efgh")
    mock_print.assert_called_with("123")



