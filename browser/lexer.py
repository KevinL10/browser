class Text:
    def __init__(self, text, parent):
        self.text = text
        # Text elements will not have children, but we include them for simplicity
        self.children = []
        self.parent = parent

    def __repr__(self):
        return self.text

class Element:
    def __init__(self, tag, parent):
        self.tag = tag
        self.children = []
        self.parent = parent

    def __repr__(self):
        return "<" + self.tag + ">"

class HTMLParser:
    def __init__(self, body):
        self.body = body
        self.unfinished = []

    # Returns a tree structure of the HTML
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

    # Adds the current text to the HTML tree
    def add_text(self, text):
        parent = self.unfinished[-1]
        node = Text(text, parent)
        parent.children.append(node)

    # Adds the current tag to the HTML tree
    def add_tag(self, tag):
        if tag.startswith("!"):
            return

        if tag.startswith("/"):
            if len(self.unfinished) == 1:
                return
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)
        else:
            parent = self.unfinished[-1] if self.unfinished else None
            node = Element(tag, parent)
            self.unfinished.append(node)

    # Finishes any unfinished nodes in the HTML tree
    def finish(self):
        if len(self.unfinished) == 0:
            self.add_tag("html")

        while len(self.unfinished) > 1:
            node = self.unfinished.pop()
            parent = self.unfinished[-1]
            parent.children.append(node)

        return self.unfinished.pop()
    

def print_tree(node, indent = 0):
    print(" " * indent, node)
    for child in node.children:
        print_tree(child, indent + 2)


k = HTMLParser("""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Document</title>
</head>
<body>
    Hi! this is a test 
    
    <b>bold text</b>
</body>
</html>""")

print_tree(k.parse())