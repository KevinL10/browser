from browser.constants import HSTEP, VSTEP, WIDTH
from browser.parser import Text, Element
import tkinter.font

FONTS = {}


def get_font(size, weight, slant):
    key = (size, weight, slant)
    if key not in FONTS:
        FONTS[(size, weight, slant)] = tkinter.font.Font(
            size=size,
            weight=weight,
            slant=slant,
        )
    return FONTS[key]


# DrawText represents a display_list command to draw text to screen
class DrawText:
    def __init__(self, x1, y1, text, font):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics("linespace")

    # Draws text to the given canvas
    def execute(self, scroll, canvas):
        canvas.create_text(
            self.left,
            self.top - scroll,
            text=self.text,
            anchor="nw",
            font=self.font,
        )


# DrawRect represents a display_list command to draw rectangles to screen
class DrawRect:
    def __init__(self, x1, y1, x2, y2, color):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color

    # Draws rectangle to the given canvas
    def execute(self, scroll, canvas: tkinter.Canvas):
        canvas.create_rectangle(
            self.left,
            self.top - scroll,
            self.right,
            self.bottom - scroll,
            width=0,  # border width
            fill=self.color,
        )


# Represents the layout of a block element
class BlockLayout:
    BLOCK_ELEMENTS = [
        "html",
        "body",
        "article",
        "section",
        "nav",
        "aside",
        "h1",
        "h2",
        "h3",
        "h4",
        "h5",
        "h6",
        "hgroup",
        "header",
        "footer",
        "address",
        "p",
        "hr",
        "pre",
        "blockquote",
        "ol",
        "ul",
        "menu",
        "li",
        "dl",
        "dt",
        "dd",
        "figure",
        "figcaption",
        "main",
        "div",
        "table",
        "form",
        "fieldset",
        "legend",
        "details",
        "summary",
    ]

    def __init__(self, node: Element, parent: Element, previous: "BlockLayout"):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []
        self.display_list = []

    def paint(self, display_list):
        bgcolor = self.node.style.get("background-color", "transparent")
        if bgcolor != "transparent":
            x2, y2 = self.x + self.width, self.y + self.height
            display_list.append(DrawRect(self.x, self.y, x2, y2, bgcolor))

        # if isinstance(self.node, Element) and self.node.tag == "pre":
        #     x2, y2 = self.x + self.width, self.y + self.height
        #     display_list.append(DrawRect(self.x, self.y, x2, y2, "gray"))

        for child in self.children:
            child.paint(display_list)

        for x, y, word, font in self.display_list:
            display_list.append(DrawText(x, y, word, font))

    """
    Returns the type of layout of the given HTML nodes
    """

    @staticmethod
    def layout_mode(node):
        if isinstance(node, Text):
            return "inline"
        elif node.children:
            if any(
                [
                    isinstance(child, Element)
                    and child.tag in BlockLayout.BLOCK_ELEMENTS
                    for child in node.children
                ]
            ):
                return "block"
            else:
                return "inline"
        else:
            return "block"

    def layout(self):
        # Compute x, y, and width from parent/previous sibling element
        self.width = self.parent.width
        self.x = self.parent.x

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        mode = BlockLayout.layout_mode(self.node)
        if mode == "block":
            previous = None
            # Create a BlockLayout for every child in the HTML tree of the current node
            for child in self.node.children:
                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next
        else:
            self.display_list = []
            self.cursor_x = 0
            self.cursor_y = 0
            self.weight = "normal"
            self.style = "roman"
            self.size = 16

            # A list of (x, word, font) tuples representing the current line
            # The final display_list is computed by aligning the words along the
            # bottom of the line
            self.line = []

            self.recurse(self.node)

            # Flushy any remaining layout elements
            self.flush()

        # Recursively layout each block child
        for child in self.children:
            child.layout()

        if mode == "block":
            self.height = sum([child.height for child in self.children])
        else:
            self.height = self.cursor_y

    """
    Recursively layout the parsed HTML tree
    """

    def recurse(self, node):
        if isinstance(node, Text):
            self.add_text(node)
        else:
            self.open_tag(node.tag)
            for child in node.children:
                self.recurse(child)
            self.close_tag(node.tag)

    """
    Updates the current weight/style/size based on the given open tag
    """

    def open_tag(self, tag):
        if tag == "i":
            self.style = "italic"
        elif tag == "b":
            self.weight = "bold"
        elif tag == "small":
            self.size -= 2
        elif tag == "big":
            self.size += 4
        elif tag == "sub":
            self.size //= 2
        elif tag == "br":
            self.flush()

    """
    Updates the current weight/style/size based on the given close tag
    """

    def close_tag(self, tag):
        if tag == "i":
            self.style = "roman"
        elif tag == "b":
            self.weight = "normal"
        elif tag == "small":
            self.size += 2
        elif tag == "big":
            self.size -= 4
        elif tag == "sub":
            self.size *= 2
        elif tag == "p":
            self.flush()
            self.cursor_y += VSTEP

    def add_text(self, token):
        font = get_font(self.size, self.weight, self.style)
        for word in token.text.split():
            w = font.measure(word)
            if self.cursor_x + w > self.width:
                self.flush()
            self.line.append((self.cursor_x, word, font))
            self.cursor_x += w + font.measure(" ")

    # Flushes the current display line:
    # - Aligns the word along the bottom of the line
    # - Add all of the words in the current line to the display_list
    # - Updates cursor_x and cursor_y
    def flush(self):
        if not self.line:
            return

        metrics = [font.metrics() for x, word, font in self.line]
        max_ascent = max([metric["ascent"] for metric in metrics])
        max_descent = max([metric["descent"] for metric in metrics])
        baseline = self.cursor_y + 1.25 * max_ascent

        for rel_x, word, font in self.line:
            x = self.x + rel_x
            y = self.y + baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = 0

        self.line = []


class DocumentLayout:
    def __init__(self, node):
        self.node = node
        self.parent = None
        self.children = []

    def paint(self, display_list):
        self.children[0].paint(display_list)

    def layout(self):
        child = BlockLayout(self.node, self, None)
        self.children.append(child)
        self.x = HSTEP
        self.y = VSTEP
        self.width = WIDTH - 2 * HSTEP
        child.layout()
        self.height = child.height + 2 * VSTEP
