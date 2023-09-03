from browser.constants import ENTITIES, MAX_REDIRECTS
import socket
import ssl
import gzip


class URL:
    # Keeps track of scheme, host, path, and port
    def __init__(self, url):
        self.url = url

        # Handle data and File URLs separatly
        if url.startswith("data:text/html"):
            self.scheme = "data"
            self.data = url.split(",", 1)[1]
            return
        elif url.startswith("file://"):
            self.scheme = "file"
            self.path = url[len("file://") :]
            return
        # elif url.startswith("view-source:"):
        #     self.scheme = "view-source"
        #     self.url = url[len("view-source:") :]

        self.scheme, url = url.split("://", 1)
        assert self.scheme in ["http", "https"], f"Unknown scheme {self.scheme}"

        # Handle no trailing slash
        if "/" in url:
            self.host, path = url.split("/", 1)
            self.path = "/" + path
        else:
            self.host = url
            self.path = "/"

        self.port = 80 if self.scheme == "http" else 443

        if ":" in self.host:
            self.host, port = self.host.split(":", 1)
            self.port = int(port)

    # Returns raw data pointed to by url
    def request(self, num_redirects=0):
        if num_redirects > MAX_REDIRECTS:
            raise Exception("Exceeded maximum number of redirects")

        if self.scheme == "file":
            with open(self.path, "r") as f:
                body = f.read()
            return None, body
        elif self.scheme == "data":
            return None, self.path

        s = socket.socket(
            family=socket.AF_INET,
            type=socket.SOCK_STREAM,
            proto=socket.IPPROTO_TCP,
        )
        print(self.host)
        s.connect((self.host, self.port))

        if self.scheme == "https":
            ctx = ssl.create_default_context()
            s = ctx.wrap_socket(s, server_hostname=self.host)
        s.send(
            f"GET {self.path} HTTP/1.1\r\n".encode("utf8")
            + f"Host: {self.host}\r\n".encode("utf8")
            + "Connection: close\r\n".encode("utf8")
            + "Accept-Encoding: gzip\r\n".encode("utf8")
            + "User-Agent: browser\r\n\r\n".encode("utf8")
        )

        response = s.makefile("rb", newline="\r\n")
        statusline = response.readline()
        version, status, explanation = statusline.split(b" ", 2)

        headers = {}

        while True:
            line = response.readline()
            if line == b"\r\n":
                break
            header, value = line.split(b":", 1)
            headers[header.lower().decode()] = value.strip().decode()

        # Handle redirects
        if 300 <= int(status) <= 399:
            return URL(headers["location"]).request(num_redirects + 1)

        assert status == b"200", f"{status}: {explanation}"
        body = response.read()

        # Support chunked transfer-encoding. Data is sent in a series of chunks, with
        # the length at the beginning of the chunk followed by \r\n, the chunk itself,
        # then a closing \r\n. The last chunk is a zero-length chunk.
        if "transfer-encoding" in headers:
            assert headers["transfer-encoding"] == "chunked"

            new_body = b""
            pos = 0
            while True:
                start = body.find(b"\r\n", pos)
                length = int(body[pos:start].decode(), 16)

                if length == 0:
                    break

                end = start + length + 2
                new_body += body[start + 2 : end]
                pos = end + 2

            body = new_body

        if "content-encoding" in headers:
            body = gzip.decompress(body)

        body = body.decode("utf-8")
        s.close()

        # For view-source schemes, we show the raw HTML output
        # by replacing reserved characters with entities
        if self.url.startswith("view-source:"):
            for entity, character in ENTITIES.items():
                body = body.replace(character, entity)
        else:
            for entity, character in ENTITIES.items():
                body = body.replace(entity, character)

        return headers, body

    # Resolve host-relative and path-relative URLs to a full URL with scheme, host, path
    def resolve(self, url):
        if "://" in url:
            return URL(url)

        if not url.startswith("/"):
            dir, _ = self.path.rsplit("/", 1)
            # Handle paths beginning with ".."
            while url.startswith("../"):
                _, url = url.split("/", 1)
                if "/" in dir:
                    dir, _ = dir.rsplit("/", 1)

            url = dir + "/" + url

        return URL(self.scheme + "://" + self.host + ":" + str(self.port) + url)

    def __repr__(self):
        port_part = ":" + str(self.port)
        if self.scheme == "https" and self.port == 443:
            port_part = ""
        elif self.scheme == "http" and self.port == 80:
            port_part = ""
        return self.scheme + "://" + self.host + port_part + self.path
