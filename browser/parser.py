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

    """
    Returns the type of tag and key-value attributes
    """

    def get_attributes(self, text):
        parts = text.split()
        if len(parts) == 1:
            return parts[0], {}

        tag = parts[0]
        attributes = {}
        for part in parts[1:]:
            if "=" in part:
                key, value = part.split("=", 1)
                if len(value) > 2 and value[0] in ["'", '"']:
                    value = value[1:-1]
                attributes[key.lower()] = value
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
    print(" " * indent, node, node.style, getattr(node, "attributes", ""))
    for child in node.children:
        print_tree(child, indent + 2)


# A parser class containing parsing functions to advance through the text
# Note: all of the functions assume no leading whitespace and strip trailing whitespace
class CSSParser:
    # Initialize the CSS parser with the text being parse and the position set to 0
    def __init__(self, s):
        self.s = s
        self.i = 0

    # Advance through the current whitespace characters
    def whitespace(self):
        while self.i < len(self.s) and self.s[self.i].isspace():
            self.i += 1

    # Advance through the current word
    def word(self):
        start = self.i
        while self.i < len(self.s):
            if self.s[self.i].isalnum() or self.s[self.i] in "#-.%":
                self.i += 1
            else:
                break

        if start == self.i:
            raise Exception("Error when parsing word")

        return self.s[start : self.i]

    # Advance through the given literal
    def literal(self, literal):
        if not (self.i < len(self.s) and self.s[self.i] == literal):
            raise Exception(f"Error when parsing literal {literal}")
        self.i += 1

    # Advance through the current property-value pair
    def pair(self):
        prop = self.word()
        self.whitespace()
        self.literal(":")
        self.whitespace()
        value = self.word()
        return prop.lower(), value

    # Advance the index unconditionally until you reach one of the chars
    def ignore_until(self, chars):
        while self.i < len(self.s):
            if self.s[self.i] in chars:
                return self.s[self.i]
            else:
                self.i += 1

    # Advance through the current "style" attribute
    def body(self):
        pairs = {}
        while self.i < len(self.s) and self.s[self.i] != "}":
            try:
                prop, value = self.pair()
                pairs[prop] = value
                self.whitespace()
                self.literal(";")
                self.whitespace()
            except Exception as e:
                print("Error parsing body:", self.s, e)  # DEBUG

                # Skip to the next set of properties if encounter parsing error
                why = self.ignore_until([";", "}"])
                if why == ";":
                    self.literal(";")
                    self.whitespace()
                else:
                    break
        return pairs

    # Advance through the current CSS selector (tag or descendant)
    def selector(self):
        out = TagSelector(self.word().lower())
        self.whitespace()
        if self.i < len(self.s) and self.s[self.i] != "{":
            out = DescendantSelector(out, TagSelector(self.word().lower()))
            self.whitespace()
        return out

    # Parse a CSS file
    def parse(self):
        rules = []
        while self.i < len(self.s):
            # Skip the whole rule if encounter parsing error
            try:
                self.whitespace()
                selector = self.selector()
                self.literal("{")
                self.whitespace()
                body = self.body()
                self.literal("}")
                rules.append((selector, body))
            except Exception:
                why = self.ignore_until(["}"])
                if why == "}":
                    self.literal("}")
                    self.whitespace()
                else:
                    break
        return rules


INHERITED_PROPERTIES = {
    "font-size": "16px",
    "font-style": "normal",
    "font-weight": "normal",
    "color": "black",
}


# Recursively add the style property-value attributes to the given node and its children
# 1. Add inherited CSS properties from default and parent
# 2. Add CSS properties from stylesheet files
# 3. Add CSS properties for element-specific style attributes
def style(node, rules):
    node.style = {}

    # Add default font properties to the current node
    # Note: this must come before specific rules in CSS files
    for property, value in INHERITED_PROPERTIES.items():
        if node.parent:
            node.style[property] = node.parent.style[property]
        else:
            node.style[property] = value

    for selector, body in rules:
        if not selector.matches(node):
            continue
        for property, value in body.items():
            node.style[property] = value

    if isinstance(node, Element) and "style" in node.attributes:
        pairs = CSSParser(node.attributes["style"]).body()
        for property, value in pairs.items():
            node.style[property] = value


    # Resolve font percentage sign
    if node.style["font-size"].endswith("%"):
        if node.parent:
            parent_font_size = node.parent.style["font-size"]
        else:
            parent_font_size = INHERITED_PROPERTIES["font-size"]

        node_pct = float(node.style["font-size"][:-1]) / 100
        parent_px = float(parent_font_size[:-2])
        node.style["font-size"] = str(parent_px * node_pct) + "px"

    for child in node.children:
        style(child, rules)


# Represents a CSS tag selector,
class TagSelector:
    def __init__(self, tag):
        self.tag = tag
        self.priority = 1

    def matches(self, node):
        return isinstance(node, Element) and self.tag == node.tag


class DescendantSelector:
    def __init__(self, ancestor, descendant):
        self.ancestor = ancestor
        self.descendant = descendant
        self.priority = self.ancestor.priority + self.descendant.priority

    def matches(self, node):
        if not self.descendant.matches(node):
            return False

        while node.parent:
            if self.ancestor.matches(node.parent):
                return True
            node = node.parent

        return False


# Returns the priority of the given CSS rule.
# Higher priority should override lower priority.
def cascade_priority(rule):
    selector, body = rule
    return selector.priority
