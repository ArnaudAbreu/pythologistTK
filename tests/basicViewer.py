# coding: utf8
from tkinter import *
from pythologistTK import view


def main():
    root = Tk()
    app = view.Viewer(root)

    # tag all of the drawn widgets
    root.mainloop()


if __name__ == "__main__":
    main()
