from browser.graphics import Browser
import sys
import tkinter

if __name__ == "__main__":

    browser = Browser()    
    if len(sys.argv) == 2:
        browser.load(sys.argv[1])
    else:
        browser.load("file:///home/vever/cs/browser/browser/tests/index.html")
        # browser.load("https://browser.engineering/layout.html")

        # browser.load("https://www.w3.org/Style/CSS/Test/CSS1/current/test5526c.htm")

    tkinter.mainloop()