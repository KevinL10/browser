from browser.constants import HSTEP, VSTEP, WIDTH
from browser.lexer import Tag, Text
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
    def __init__(self, tokens):
        self.display_list = []
        self.cursor_x = HSTEP
        self.cursor_y = VSTEP
        self.weight = "normal"
        self.style = "roman"
        self.size = 16

        # Text is aligned along the top by default (instead of the bottom), so
        # we use a two-pass approach: first compute the x-coordinates of the
        # elements along the current line, then adjust the y-coordinates so that
        # all elements are aligned along the bottom
        self.line = []

        for token in tokens:
            self.add_token(token)

        # Flushy any remaining layout elements
        self.flush()


    def add_token(self, token):
        if isinstance(token, Text):
            self.add_text(token)
        elif token.tag == "i":
            self.style = "italic"
        elif token.tag == "/i":
            self.style = "roman"
        elif token.tag == "b":
            self.weight = "bold"
        elif token.tag == "/b":
            self.weight = "normal"
        elif token.tag == "small":
            self.size -= 2
        elif token.tag == "/small":
            self.size += 2
        elif token.tag == "big":
            self.size += 4
        elif token.tag == "/big":
            self.size -= 4
        elif token.tag == "br":
            self.flush()
        elif token.tag == "/p":
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
