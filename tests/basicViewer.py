# coding: utf8
from tkinter import *
from tkinter import ttk
from ttkthemes import ThemedStyle
from tkinter.filedialog import *
from pythologistTK import model
import os


def main():
    root = Tk()
    style = ThemedStyle(root)
    style.set_theme("black")

    app = model.Model(root)

    # tag all of the drawn widgets
    root.mainloop()


if __name__ == "__main__":
    main()
