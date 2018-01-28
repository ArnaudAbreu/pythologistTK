# coding: utf8
from tkinter import *
from tkinter import ttk
from ttkthemes import ThemedStyle
from tkinter.filedialog import *
from pythologistTK import view, annotation


class Application:
    def __init__(self, master):

        self.master = master

        # Menu bar
        self.menubar = Menu(self.master)

        # File Menu
        self.file_menu = Menu(self.menubar)
        self.file_menu.add_command(label="Open Image",
                                   command=self.open_image_file)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        # link the menu to the app
        self.master.config(menu=self.menubar)

        self.nb = ttk.Notebook(self.master, height=800, width=800)
        self.nb.pack(fill=BOTH, expand=YES)

        # Adds tab 1 of the notebook
        self.page1 = ttk.Frame(self.nb)
        self.nb.add(self.page1, text='Viewer')

        # Adds tab 2 of the notebook
        self.page2 = ttk.Frame(self.nb)
        self.nb.add(self.page2, text='Annotation')

        # Adds tab 3 of the notebook
        self.page3 = ttk.Frame(self.nb)
        self.nb.add(self.page3, text='Stats')

        self.annotapp = annotation.AnnotationTab(self.page2)
        self.app = view.ViewerTab(self.page1, self.master)

    def open_image_file(self):
        # get path of the slide
        filepath = askopenfilename(title="open image",
                                   filetypes=[('mrxs files', '.mrxs'),
                                              ('all files', '.*')])
        self.app.open_image_file(filepath)

        annotationfile = filepath[0:-len(".mrxs")] + ".annot"

        self.annotapp.open_annotations_file(annotationfile)


def main():
    root = Tk()
    style = ThemedStyle(root)
    style.set_theme("black")

    app = Application(root)

    # tag all of the drawn widgets
    root.mainloop()


if __name__ == "__main__":
    main()
