class Text:
    def __init__(self, text, parent):
        self.text = text
        # Text elements will not have children, but we include them for simplicity
        self.children = []
        self.parent = parent

    def __repr__(self):
        return self.text


class Element:
    def __init__(self, tag, attributes, parent):
        self.tag = tag
        self.attributes = attributes
        self.children = []
        self.parent = parent

    def __repr__(self):
        return "<" + self.tag + ">"


"""
We represent the document as a list of unfinished open tags. When we encounter a 
closing tag, we remove the topmost tag from the list and add it as a child of the 
previous tag.
"""


class HTMLParser:
    def __init__(self, body):
        self.body = body
        self.unfinished = []
        self.SELF_CLOSING_TAGS = [
            "area",
            "base",
            "br",
            "col",
            "embed",
            "hr",
            "img",
            "input",
            "link",
            "meta",
            "param",
            "source",
            "track",
            "wbr",
        ]

    """
    Returns a tree structure of the HTML.
    """

    def parse(self):
        in_tag = False
        text = ""

        for c in self.body:
            if c == "<":
                in_tag = True
                if text:
                    self.add_text(text)
                text = ""
            elif c == ">":
                in_tag = False
                self.add_tag(text)
                text = ""
            else:
                text += c

        if not in_tag and text:
            self.add_text(text)

        return self.finish()

    '''
    Returns the type of tag and key-value attributes
    '''
    def get_attributes(self, text):
        parts = text.split()
        if len(parts) == 1:
            return parts[0], {}

        print(parts)
        tag = parts[0]
        attributes = {}
        for part in parts[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                if len(value) > 2 and value[0] in ["'", "\""]:
                    value = value[1:-1]
            else:
                attributes[part.lower()] = ""
        return tag, attributes

    """
    Adds the given text as a child of the current open tag.
    """

    def add_text(self, text):
        if text.isspace():
            return
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    """
    Adds the current tag to the HTML tree. If the tag is open, add it to the list of 
    unfinished tags. Otherwise, close the topmost tag.
    """

    def add_tag(self, tag):
        tag, attributes = self.get_attributes(tag)
        # ignore DOCTYPE tag (<!DOCTYPE html> and comments (<!-- ... -->)
        if tag.startswith("!"):
            return

        if tag.startswith("/"):
            if len(self.unfinished) == 1:
                return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        elif tag in self.SELF_CLOSING_TAGS:
            parent = self.unfinished[-1]
            node = Element(tag, attributes, parent)
            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, attributes, parent)
            self.unfinished.append(node)

    """
    Closes any remaining open tags in the HTML tree and returns the root node.
    """

    def finish(self):
        if len(self.unfinished) == 0:
            self.add_tag("html")

        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)

        return self.unfinished.pop()


def print_tree(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)


# k = HTMLParser(
#     """<!DOCTYPE html>
# <html lang="en">
# <head>
#     <meta charset="UTF-8">
#     <meta http-equiv="X-UA-Compatible" content="IE=edge">
#     <meta name="viewport" content="width=device-width, initial-scale=1.0">
#     <title>Document</title>
# </head>
# <body>
#     Hi! this is a test 
#     <b>bold text</b>
# </body>
# </html>"""
# )

# print_tree(k.parse())
