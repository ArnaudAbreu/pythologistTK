# coding: utf8
from tkinter import *
from tkinter import ttk
from ttkthemes import ThemedStyle
from pythologistTK import view


def main():
    root = Tk()
    style = ThemedStyle(root)
    style.set_theme("black")

    nb = ttk.Notebook(root)
    nb.pack(fill=BOTH, expand=YES)

    # Adds tab 1 of the notebook
    page1 = ttk.Frame(nb)
    nb.add(page1, text='Viewer')

    # Adds tab 2 of the notebook
    page2 = ttk.Frame(nb)
    nb.add(page2, text='Process')

    # Adds tab 3 of the notebook
    page3 = ttk.Frame(nb)
    nb.add(page3, text='Stats')

    app = view.ViewerTab(page1, root)

    # tag all of the drawn widgets
    root.mainloop()


if __name__ == "__main__":
    main()
