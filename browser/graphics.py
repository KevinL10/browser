from browser.parser import HTMLParser
from browser.request import request
from browser.constants import VSTEP, HEIGHT, WIDTH, SCROLL_STEP
from browser.layout import DocumentLayout
import tkinter
import tkinter.font


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(self.window, width=WIDTH, height=HEIGHT)
        self.canvas.pack()
        self.scroll = 0

        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Down>", self.scrolldown)

        # Linux mouse wheel bindings
        self.window.bind("<Button-4>", self.scrollup)
        self.window.bind("<Button-5>", self.scrolldown)

    def scrollup(self, e):
        self.scroll = max(0, self.scroll - SCROLL_STEP)
        self.draw()

    def scrolldown(self, e):
        # Prevent scrolling past bottom of the page
        max_y = max(self.document.height - HEIGHT, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)
        self.draw()


    # Draws the to-be-displayed text; calculates the position
    # of each character by subtracting the current scroll
    # (i.e. how far the user is down the page)
    def draw(self):
        self.canvas.delete("all")
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT:
                continue
            if cmd.bottom + VSTEP < self.scroll:
                continue

            cmd.execute(self.scroll, self.canvas)


    # Renders the contents of the url to the canvas
    def load(self, url):
        headers, body = request(url)
        self.nodes = HTMLParser(body).parse()
        self.document = DocumentLayout(self.nodes)
        self.document.layout()

        # The display_list consists of commands like DrawText and DrawRect
        self.display_list = []
        self.document.paint(self.display_list)
        self.draw()


# Browser().load("file:///home/vever/cs/browser/browser/tests/index.html")

# Browser().load("file://./tests/index.html")
# Browser().load("https://browser.engineering/redirect")
# Browser().load("https://browser.engineering/http.html")
# tkinter.mainloop()
