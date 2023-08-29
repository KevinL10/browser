from browser.graphics import Browser
from browser.request import URL
import sys
import tkinter

if __name__ == "__main__":

    browser = Browser()    
    if len(sys.argv) == 2:
        browser.load(URL(sys.argv[1]))
    else:
        browser.load(URL("https://browser.engineering/styles.html"))

        # browser.load("https://www.w3.org/Style/CSS/Test/CSS1/current/test5526c.htm")

    tkinter.mainloop()