import socket
import ssl


# Returns: scheme, host, port, data (could be a path or raw HTML depending on scheme)
def parse_url(url):
    # Handle data and File URLs separatly
    if url.startswith("data:text/html"):
        scheme, data = url.split(",", 1)
        return "data", None, None, data
    elif url.startswith("file://"):
        return "file", None, None, url[len("file://") :]

    scheme, url = url.split("://", 1)
    assert scheme in ["http", "https"], f"Unknown scheme {scheme}"

    # Handle no trailing slash
    if "/" in url:
        host, path = url.split("/", 1)
        path = "/" + path
    else:
        host = url
        path = "/"

    port = 80 if scheme == "http" else 443

    if ":" in host:
        host, port = host.split(":", 1)
        port = int(port)

    return scheme, host, port, path


# Returns data pointed to by url
def request(url):
    scheme, host, port, path = parse_url(url)

    if scheme == "file":
        with open(path, "r") as f:
            body = f.read()
        return None, body
    elif scheme == "data":
        return None, path

    s = socket.socket(
        family=socket.AF_INET,
        type=socket.SOCK_STREAM,
        proto=socket.IPPROTO_TCP,
    )

    s.connect((host, port))

    if scheme == "https":
        ctx = ssl.create_default_context()
        s = ctx.wrap_socket(s, server_hostname=host)
    s.send(
        f"GET {path} HTTP/1.1\r\n".encode("utf8")
        + f"Host: {host}\r\n".encode("utf8")
        + f"Connection: close\r\n".encode("utf8")
        + f"User-Agent: browser\r\n\r\n".encode("utf8")
    )

    response = s.makefile("r", encoding="utf8", newline="\n")
    statusline = response.readline()
    version, status, explanation = statusline.split(" ", 2)

    assert status == "200", f"{status}: {explanation}"

    headers = {}

    while True:
        line = response.readline()
        if line == "\r\n":
            break
        header, value = line.split(":", 1)
        headers[header.lower()] = value.strip()

    assert "transfer-encoding" not in headers
    assert "content-encoding" not in headers

    body = response.read()
    s.close()

    return headers, body


def show(body):
    in_angle = False
    for c in body:
        if c == "<":
            in_angle = True
        elif c == ">":
            in_angle = False
        elif not in_angle:
            print(c, end="")


def load(url):
    headers, body = request(url)
    show(body)


if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2:
        load(sys.argv[1])
    else:
        load("https://example.org")
