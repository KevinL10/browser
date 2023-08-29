from browser.parser import (
    HTMLParser,
    CSSParser,
    style,
    Element,
    cascade_priority,
    Text,
)
from browser.constants import VSTEP, HEIGHT, WIDTH, SCROLL_STEP
from browser.layout import DocumentLayout, print_layout
from browser.utils import tree_to_list
import tkinter
import tkinter.font


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, width=WIDTH, height=HEIGHT, bg="white"
        )
        self.canvas.pack()
        self.scroll = 0

        self.url = None

        self.window.bind("<Up>", self.scrollup)
        self.window.bind("<Down>", self.scrolldown)

        # Click binding
        self.window.bind("<Button-1>", self.click)

        # Linux mouse wheel bindings
        self.window.bind("<Button-4>", self.scrollup)
        self.window.bind("<Button-5>", self.scrolldown)

        with open("tests/browser.css", "r") as f:
            self.default_style_sheet = CSSParser(f.read()).parse()

    def scrollup(self, e):
        self.scroll = max(0, self.scroll - SCROLL_STEP)
        self.draw()

    def scrolldown(self, e):
        # Prevent scrolling past bottom of the page
        max_y = max(self.document.height - HEIGHT, 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)
        self.draw()

    # Handle clicking on links (i.e. <a href=...> elements)
    def click(self, e):
        # Note that e.x and e.y are relative to the browser window
        # so we must add the self.scroll amount to y
        x, y = e.x, e.y
        y += self.scroll

        # TODO: find a faster way to calculate which element is clicked
        objs = [
            obj
            for obj in tree_to_list(self.document, [])
            if obj.x <= x < obj.x + obj.width and obj.y <= y < obj.y + obj.height
        ]

        if not objs:
            return

        # Take the most specific element (i.e. the last one, usually a text node)
        # Then, find any <a href=...> elements in the parent chain
        element = objs[-1].node
        while element:
            if isinstance(element, Text):
                pass
            elif element.tag == "a" and "href" in element.attributes:
                url = self.url.resolve(element.attributes["href"])
                return self.load(url)

            element = element.parent

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
        self.url = url
        headers, body = url.request()
        self.node = HTMLParser(body).parse()

        links = [
            node.attributes["href"]
            for node in tree_to_list(self.node, [])
            if isinstance(node, Element)
            and node.tag == "link"
            and node.attributes.get("rel") == "stylesheet"
            and "href" in node.attributes
        ]

        rules = self.default_style_sheet.copy()

        for link in links:
            head, body = url.resolve(link).request()
            rules.extend(CSSParser(body).parse())

        # Sort first by CSS priority, then by file order
        # Higher priority rules will come later in the rules array
        style(self.node, sorted(rules, key=cascade_priority))

        self.document = DocumentLayout(self.node)
        self.document.layout()

        print_layout(self.document)

        # The display_list consists of commands like DrawText and DrawRect
        self.display_list = []
        self.document.paint(self.display_list)
        self.draw()


# Browser().load("file:///home/vever/cs/browser/browser/tests/index.html")

# Browser().load("file://./tests/index.html")
# Browser().load("https://browser.engineering/redirect")
# Browser().load("https://browser.engineering/http.html")
# tkinter.mainloop()
