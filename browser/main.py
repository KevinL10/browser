from browser.request import load

if __name__ == "__main__":
    import sys

    if len(sys.argv) == 2:
        load(sys.argv[1])
    else:
        load("https://example.org")
