from browser.graphics import Browser
import sys
import tkinter

if __name__ == "__main__":

    browser = Browser()    
    if len(sys.argv) == 2:
        browser.load(sys.argv[1])
    else:
        browser.load("https://example.org")

    tkinter.mainloop()