from browser.util import lex
from browser.request import request
from browser.constants import HSTEP, VSTEP, HEIGHT, WIDTH, SCROLL_STEP
import tkinter


class Browser:
    def __init__(self):
        self.window = tkinter.Tk()
        self.canvas = tkinter.Canvas(
            self.window, 
            width=WIDTH,
            height=HEIGHT
        )
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
        self.scroll += SCROLL_STEP
        self.draw()

    # Returns the coordinates (relative to start of the PAGE)
    # for each character of the text
    def layout(self, text):
        display_list = []
        cursor_x, cursor_y = HSTEP, VSTEP
        for c in text:
            display_list.append((cursor_x, cursor_y, c))
            cursor_x += HSTEP

            if cursor_x >= WIDTH - HSTEP:
                cursor_x = HSTEP
                cursor_y += VSTEP
        return display_list

    # Draws the to-be-displayed text; calculates the position
    # of each character by subtracting the current scroll
    # (i.e. how far the user is down the page)
    def draw(self):
        self.canvas.delete("all")
        for x, y, c in self.display_list:
            if y > self.scroll + HEIGHT:
                continue
            if y + VSTEP < self.scroll:
                continue
            self.canvas.create_text(x, y - self.scroll, text=c)

    # Renders the contents of the url to the canvas
    def load(self, url):
        headers, body = request(url)
        text = lex(body)
        

        self.display_list = self.layout(text)
        self.draw()
        


Browser().load('https://browser.engineering/examples/xiyouji.html')
tkinter.mainloop()


