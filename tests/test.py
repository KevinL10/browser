from browser.main import *

def test_parse_file_url():
    headers, body = request("data:text/html,Hello world!")

    assert body == "Hello world!"
