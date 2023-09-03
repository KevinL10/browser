from browser.parser import (
    HTMLParser,
    CSSParser,
    style,
    Element,
    cascade_priority,
    Text,
)
from browser.constants import VSTEP, HEIGHT, WIDTH, SCROLL_STEP
from browser.layout import (
    DocumentLayout,
    DrawRect,
    DrawLine,
    DrawText,
    DrawOutline,
    get_font,
    print_layout
)
from browser.utils import tree_to_list
from browser.request import URL
import tkinter
import tkinter.font

# Reserve space for the tab bar at the top
CHROME_PX = 100


class Tab:
    def __init__(self):
        self.scroll = 0
        self.url = None
        self.history = []

        with open("tests/browser.css", "r") as f:
            self.default_style_sheet = CSSParser(f.read()).parse()

    def scrollup(self):
        self.scroll = max(0, self.scroll - SCROLL_STEP)

    def scrolldown(self):
        # Prevent scrolling past bottom of the page
        max_y = max(self.document.height - (HEIGHT - CHROME_PX), 0)
        self.scroll = min(self.scroll + SCROLL_STEP, max_y)

    # Handle clicking on links (i.e. <a href=...> elements)
    def click(self, x, y):
        # Note that e.x and e.y are relative to the browser window
        # so we must add the self.scroll amount to y
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

    def draw(self, canvas):
        for cmd in self.display_list:
            if cmd.top > self.scroll + HEIGHT - CHROME_PX:
                continue
            if cmd.bottom + VSTEP < self.scroll:
                continue

            cmd.execute(self.scroll - CHROME_PX, canvas)

    # Renders the contents of the url to the canvas
    def load(self, url):
        self.history.append(url)
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

        # print_tree(self.node)
        print_layout(self.document)

        # The display_list consists of commands like DrawText and DrawRect
        self.display_list = []
        self.document.paint(self.display_list)

    def go_back(self):
        if len(self.history) > 1:
            self.history.pop()
            back = self.history.pop()
            self.load(back)


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, width=WIDTH, height=HEIGHT, bg="white"
        )
        self.canvas.pack()

        self.window.bind("<Up>", self.handle_up)
        self.window.bind("<Down>", self.handle_down)

        # Click binding
        self.window.bind("<Button-1>", self.handle_click)

        # Linux mouse wheel bindings
        self.window.bind("<Button-4>", self.handle_up)
        self.window.bind("<Button-5>", self.handle_down)

        self.window.bind("<Key>", self.handle_key)
        self.window.bind("<Return>", self.handle_enter)

        self.tabs = []
        self.active_tab = None

        self.focus = None
        self.address_bar = ""

    def handle_up(self, e):
        self.tabs[self.active_tab].scrollup()
        self.draw()

    def handle_down(self, e):
        self.tabs[self.active_tab].scrolldown()
        self.draw()

    def handle_click(self, e):
        if e.y < CHROME_PX:
            if 40 <= e.x < 40 + 80 * len(self.tabs) and 0 <= e.y < 40:
                self.active_tab = int((e.x - 40) / 80)
            elif 10 <= e.x < 30 and 10 <= e.y < 30:
                self.load(URL("https://browser.engineering/"))
            elif 10 <= e.x < 35 and 50 <= e.y < 90:
                self.tabs[self.active_tab].go_back()
            elif 50 <= e.x < WIDTH - 10 and 50 <= e.y < 90:
                self.focus = "address_bar"
                self.address_bar = ""
        else:
            self.tabs[self.active_tab].click(e.x, e.y - CHROME_PX)
        self.draw()

    def handle_key(self, e):
        if len(e.char) == 0:
            return

        if not (0x20 <= ord(e.char) < 0x7F or ord(e.char) == 8):
            return

        if self.focus == "address_bar":
            if ord(e.char) == 8:
                self.address_bar = self.address_bar[:-1]
            else:
                self.address_bar += e.char
            self.draw()

    def handle_enter(self, e):
        if self.focus == "address_bar":
            self.tabs[self.active_tab].load(URL(self.address_bar))
            self.focus = None
            self.draw()

    def draw(self):
        self.canvas.delete("all")
        self.tabs[self.active_tab].draw(self.canvas)

        # Draw the browser chrome (tabs, icons, buttons, etc.)
        for cmd in self.paint_chrome():
            cmd.execute(0, self.canvas)

    def paint_chrome(self):
        cmds = []
        cmds.append(DrawRect(0, 0, WIDTH, CHROME_PX, "white"))
        cmds.append(DrawLine(0, CHROME_PX - 1, WIDTH, CHROME_PX - 1, "black", 1))

        tabfont = get_font(20, "normal", "roman")

        for i, tab in enumerate(self.tabs):
            name = f"Tab {i}"
            x1, x2 = 40 + 80 * i, 120 + 80 * i

            # Create tab borders
            cmds.append(DrawRect(x1, 0, x1, 40, "black"))
            cmds.append(DrawRect(x2, 0, x2, 40, "black"))
            cmds.append(DrawText(x1 + 10, 10, name, tabfont, "black"))

            # Draw the "popup" effect for the current active tab
            if i == self.active_tab:
                cmds.append(DrawLine(0, 40, x1, 40, "black", 1))
                cmds.append(DrawLine(x2, 40, WIDTH, 40, "black", 1))

        # Draw the "+" button to add a new tab
        buttonfont = get_font(20, "normal", "roman")
        cmds.append(DrawOutline(10, 10, 30, 30, "black", 1))
        cmds.append(DrawText(11, 0, "+", buttonfont, "black"))

        # Draw either the URL or the current typed address in the address_bar
        cmds.append(DrawOutline(40, 50, WIDTH - 10, 90, "black", 1))
        if self.focus == "address_bar":
            w = buttonfont.measure(self.address_bar)
            cmds.append(DrawLine(55 + w, 55, 55 + w, 85, "black", 1))
            cmds.append(DrawText(55, 55, self.address_bar, buttonfont, "black"))
        else:
            url = str(self.tabs[self.active_tab].url)
            cmds.append(DrawText(55, 55, url, buttonfont, "black"))

        # Draw the back button
        cmds.append(DrawOutline(10, 50, 35, 90, "black", 1))
        cmds.append(DrawText(15, 50, "<", buttonfont, "black"))
        return cmds

    # Renders the contents of the url to the canvas
    def load(self, url):
        new_tab = Tab()
        new_tab.load(url)

        self.active_tab = len(self.tabs)
        self.tabs.append(new_tab)
        self.draw()


# Browser().load("file:///home/vever/cs/browser/browser/tests/index.html")

# Browser().load("file://./tests/index.html")
# Browser().load("https://browser.engineering/redirect")
# Browser().load("https://browser.engineering/http.html")
# tkinter.mainloop()
