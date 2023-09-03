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
    def __init__(self, x1, y1, text, font, color):
        self.top = y1
        self.left = x1
        self.text = text
        self.font = font
        self.bottom = y1 + font.metrics("linespace")
        self.color = color

    # Draws text to the given canvas
    def execute(self, scroll, canvas):
        canvas.create_text(
            self.left,
            self.top - scroll,
            text=self.text,
            anchor="nw",
            font=self.font,
            fill=self.color,
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


class DrawLine:
    def __init__(self, x1, y1, x2, y2, color, thickness):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color
        self.thickness = thickness

    def execute(self, scroll, canvas):
        canvas.create_line(
            self.left,
            self.top - scroll,
            self.right,
            self.bottom - scroll,
            fill=self.color,
            width=self.thickness,
        )


class DrawOutline:
    def __init__(self, x1, y1, x2, y2, color, thickness):
        self.top = y1
        self.left = x1
        self.bottom = y2
        self.right = x2
        self.color = color
        self.thickness = thickness

    def execute(self, scroll, canvas):
        canvas.create_rectangle(
            self.left,
            self.top - scroll,
            self.right,
            self.bottom - scroll,
            width=self.thickness,
            outline=self.color,
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

    def __repr__(self):
        if isinstance(self.node, Text):
            return "<BlockLayout text>"
        else:
            return f"<BlockLayout tag={self.node.tag}>"

    def paint(self, display_list):
        bgcolor = self.node.style.get("background-color", "transparent")
        if bgcolor != "transparent":
            x2, y2 = self.x + self.width, self.y + self.height
            display_list.append(DrawRect(self.x, self.y, x2, y2, bgcolor))

        for child in self.children:
            child.paint(display_list)

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
                # Don't add the <head> tag to the layout tree
                if isinstance(child, Element) and child.tag == "head":
                    continue

                next = BlockLayout(child, self, previous)
                self.children.append(next)
                previous = next
        else:
            self.new_line()
            self.recurse(self.node)

        # Recursively layout each block child
        for child in self.children:
            child.layout()

        # If block-mode, then the height is the sum of its children HTML elements
        # Otherwise, if inline-mode, then the height is the sum of the children
        # LineLayout objects
        self.height = sum([child.height for child in self.children])

    """
    Recursively layout the parsed HTML tree
    """

    def recurse(self, node):
        if isinstance(node, Text):
            for word in node.text.split():
                self.word(node, word)
        else:
            if node.tag == "br":
                self.new_line()

            for child in node.children:
                self.recurse(child)

    # Add the word in the current node to the display list
    def word(self, node, word):
        font = self.get_font(node)
        w = font.measure(word)

        if self.cursor_x + w > self.width:
            self.new_line()

        # Add the word to the current LineLayout object
        line = self.children[-1]
        text = TextLayout(node, word, line, self.previous_word)
        line.children.append(text)
        self.previous_word = text

        self.cursor_x += w + font.measure(" ")

    # Creates a new line object
    def new_line(self):
        self.previous_word = None
        self.cursor_x = 0

        previous_line = self.children[-1] if self.children else None
        self.children.append(LineLayout(self.node, self, previous_line))

    # Return the font corresponding to the current node's style attributes
    def get_font(self, node):
        weight = node.style["font-weight"]
        style = node.style["font-style"]
        font_size = int(float(node.style["font-size"][:-2]) * 0.75)

        # Translate to Tk units
        if style == "normal":
            style = "roman"

        return get_font(font_size, weight, style)


# Stores the layout for a line of words
class LineLayout:
    def __init__(self, node, parent, previous):
        self.node = node
        self.parent = parent
        self.previous = previous
        self.children = []

    def __repr__(self):
        return "<LineLayout>"

    def layout(self):
        self.width = self.parent.width
        self.x = self.parent.x

        if self.previous:
            self.y = self.previous.y + self.previous.height
        else:
            self.y = self.parent.y

        # Layout each of the words (TextLayout objects) in the current line
        for word in self.children:
            word.layout()

        # TODO: how should you handle the case of multiple <br> tags in a row?
        if not self.children:
            self.height = 0
            return

        metrics = [word.font.metrics() for word in self.children]
        max_ascent = max([metric["ascent"] for metric in metrics])
        max_descent = max([metric["descent"] for metric in metrics])
        baseline = self.y + 1.25 * max_ascent

        for word in self.children:
            word.y = baseline - word.font.metrics("ascent")

        self.height = 1.25 * (max_ascent + max_descent)

    # Paints all of the children TextLayout objects
    def paint(self, display_list):
        for child in self.children:
            child.paint(display_list)


# Stores the layout for a single word
class TextLayout:
    def __init__(self, node, word, parent, previous):
        self.node = node
        self.word = word
        self.parent = parent
        self.previous = previous
        self.children = []

    def __repr__(self):
        return f'<TextLayout word="{self.word}">'

    # Layout the current text object by computing its font, x, width, and height
    # Note: the text's y coordinate is already computed by the LineLayout object
    def layout(self):
        weight = self.node.style["font-weight"]
        style = self.node.style["font-style"]
        font_size = int(float(self.node.style["font-size"][:-2]) * 0.75)

        # Convert to tkinter
        if style == "normal":
            style = "roman"

        self.font = get_font(font_size, weight, style)

        # Compute the position and dimensions of the word
        self.width = self.font.measure(self.word)

        if self.previous:
            self.x = self.previous.x + self.previous.width + self.font.measure(" ")
        else:
            self.x = self.parent.x

        self.height = self.font.metrics("linespace")

    # Paints the current word to the display list
    def paint(self, display_list):
        color = self.node.style["color"]
        display_list.append(DrawText(self.x, self.y, self.word, self.font, color))


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


def print_layout(node, indent=0):
    print(" " * indent, node)
    for child in node.children:
        print_layout(child, indent + 2)
