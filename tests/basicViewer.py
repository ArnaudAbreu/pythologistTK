# coding: utf8
from tkinter import *
from tkinter import ttk
from ttkthemes import ThemedStyle
from tkinter.filedialog import *
from pythologistTK import model
import os
from tkinter import messagebox


def main():
    root = Tk()
    style = ThemedStyle(root)
    style.set_theme("black")
    root.title("Pythologist")

    app = model.Model(root)

    def checkbeforeleaving():
        if messagebox.askyesno("Overwrite annotation file ?"):
            app.saveAnnotations()
        root.destroy()

    root.protocol("WM_DELETE_WINDOW", checkbeforeleaving)

    # tag all of the drawn widgets
    root.mainloop()


if __name__ == "__main__":
    main()
