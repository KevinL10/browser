from browser.constants import HSTEP, VSTEP, WIDTH
from browser.lexer import Text
import tkinter.font

FONTS = {}


def get_font(size, weight, slant):
    key = (size, weight, slant)
    if key not in FONTS:
        FONTS[(size, weight, slant)] = tkinter.font.Font(
            family="Times",
            size=size,
            weight=weight,
            slant=slant,
        )
    return FONTS[key]

# Represents the layout of the web page (including font, position, size, etc.)
class Layout:
    def __init__(self, node):
        self.display_list = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 16

        # A list of (x, word, font) tuples representing the current line
        # The final display_list is computed by aligning the words along the
        # bottom of the line
        self.line = []

        self.recurse(node)

        # Flushy any remaining layout elements
        self.flush()

    '''
    Recursively layout the parsed HTML tree
    '''
    def recurse(self, node):
        if isinstance(node, Text):
            self.add_text(node)
        else:
            self.open_tag(node.tag)
            for child in node.children:
                self.recurse(child)
            self.close_tag(node.tag)
    
    '''
    Updates the current weight/style/size based on the given open tag
    '''
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

    '''
    Updates the current weight/style/size based on the given close tag
    '''
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

            if self.cursor_x + w >= WIDTH - HSTEP:
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
        baseline = self.cursor_y + max_ascent

        for x, word, font in self.line:
            y = baseline - font.metrics("ascent")
            self.display_list.append((x, y, word, font))

        self.cursor_y = baseline + 1.25 * max_descent
        self.cursor_x = HSTEP

        self.line = []
