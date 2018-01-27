# coding: utf8
"""
Viewer classes
Original author: Arnaud Abreu
"""
from tkinter import *
from tkinter.filedialog import *
from PIL import Image, ImageTk
from openslide import OpenSlide
import pickle
import numpy
from scipy.misc import imsave


class ResizeableCanvas(Canvas):
    """
    A class extending the tkinter Canvas class and enabling resizing
    """
    def __init__(self, parent, **kwargs):
        Canvas.__init__(self, parent, **kwargs)
        self.bind("<Configure>", self.on_resize)
        self.height = self.winfo_reqheight()
        self.width = self.winfo_reqwidth()

    def on_resize(self, event):
        # determine the ratio of old width/height to new width/height
        wscale = float(event.width) / self.width
        hscale = float(event.height) / self.height
        self.width = event.width
        self.height = event.height
        # resize the canvas
        self.config(width=self.width, height=self.height)


class Viewer:
    """
    A simple Viewer class
    """
    def __init__(self, master, dim=800):

        self.tool = "slide"

        self.xref = 0
        self.yref = 0

        self.master = master
        self.master.wm_title("Pythologist")

        # Menu bar
        self.menubar = Menu(self.master)

        # File Menu
        self.file_menu = Menu(self.menubar)
        self.file_menu.add_command(label="Open Image",
                                   command=self.open_image_file)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        # link the menu to the app
        self.master.config(menu=self.menubar)

        # image container
        self.canvas = ResizeableCanvas(self.master, width=dim, height=dim, highlightthickness=0)
        self.canvas.pack(fill=BOTH, expand=YES)

        # canvas bind events
        self.canvas.bind("<Button-1>", self.dirbutton)
        self.canvas.bind("<B1-Motion>", self.move)
        self.canvas.bind("<ButtonRelease-1>", self.nomove)

        # have to create frames to put buttons inside and make it pretty
        # self.zoompanel = LabelFrame(self.master, text="Zoom panel", padx=20, pady=20)
        self.buttonzoom = Button(self.canvas, text="Zoom", command=self.zoom,
                                 relief=FLAT)
        self.buttondezoom = Button(self.canvas, text="Dezoom", command=self.dezoom,
                                   relief=FLAT)

        # self.zoombuttonwindow = self.canvas.create_window(10, 10, anchor='nw', window=self.buttonzoom)

        # packing everything
        # self.zoombuttonwindow.pack()
        # self.buttonzoom.pack()
        # self.buttondezoom.pack()

    def open_image_file(self):
        """
        A function that create the image in the canvas
        and initialize several variables
        """
        # if there is an image in the canvas, delete it
        self.canvas.delete('all')

        # get path of the slide
        filepath = askopenfilename(title="open image",
                                   filetypes=[('mrxs files', '.mrxs'),
                                              ('tiff files', '.tif'),
                                              ('all files', '.*')])

        # define slide object
        self.slide = OpenSlide(filepath)

        # define current level of observation to lowest level (highest on pyramid)
        self.level = self.slide.level_count - 1
        print("nombre de niveaux dans la pyramide : ", self.level)

        # create an image low resolution to find ROI in current level
        im = numpy.asarray(self.slide.read_region(location=(0, 0),
                                                  level=self.level,
                                                  size=self.slide.level_dimensions[self.level]))

        # find ROI in current level
        [i, j] = numpy.where(im[:, :, 0] > 0)

        # center of ROI in current level
        ci = round(numpy.mean(i))
        cj = round(numpy.mean(j))
        ci = int(ci)
        cj = int(cj)

        # image position in current level
        ci -= int(self.canvas.height + (self.canvas.height / 2))
        cj -= int(self.canvas.width + (self.canvas.width / 2))

        # image absolute position in slide
        self.image_y_abs = ci * numpy.power(2, self.level)
        self.image_x_abs = cj * numpy.power(2, self.level)

        # image creation
        self.image = self.slide.read_region(location=(self.image_x_abs,
                                                      self.image_y_abs),
                                            level=self.level,
                                            size=(3 * self.canvas.width,
                                                  3 * self.canvas.height))
        self.image.putalpha(255)

        # create canvas image from PIL image
        self.photoimage = ImageTk.PhotoImage(self.image)
        self.canvas.delete("image")
        self.canvas.create_image(-self.canvas.width, -self.canvas.height,
                                 anchor=NW, image=self.photoimage, tags="image")
        self.buttonzoomwindow = self.canvas.create_window(self.canvas.width -
                                                          100,
                                                          50, width=100,
                                                          height=25,
                                                          window=self.buttonzoom)
        self.buttondezoomwindow = self.canvas.create_window(self.canvas.width -
                                                            100,
                                                            100, width=100,
                                                            height=25,
                                                            window=self.buttondezoom)
        print("open image file")

    def abscenter(self):
        abscenterx = self.image_x_abs + int(self.canvas.width + (self.canvas.width / 2)) * numpy.power(2, self.level)
        abscentery = self.image_y_abs + int(self.canvas.height + (self.canvas.height / 2)) * numpy.power(2, self.level)
        return abscenterx, abscentery

    def redraw(self, x, y):
        self.image_x_abs = x - int(self.canvas.width + (self.canvas.width / 2)) * numpy.power(2, self.level)
        self.image_y_abs = y - int(self.canvas.height + (self.canvas.height / 2)) * numpy.power(2, self.level)

        # get image position in canvas at new level
        self.image = self.slide.read_region(location=(self.image_x_abs,
                                                      self.image_y_abs),
                                            level=self.level,
                                            size=(3 * self.canvas.width,
                                                  3 * self.canvas.height))
        self.image.putalpha(255)
        self.photoimage = ImageTk.PhotoImage(self.image)
        self.canvas.delete("image")
        self.canvas.create_image(-self.canvas.width, -self.canvas.height,
                                 anchor=NW, image=self.photoimage, tags="image")
        self.canvas.pack()

    def dirbutton(self, event):
        if self.tool == "slide":
            self.xref = event.x
            self.yref = event.y

    def move(self, event):
        if self.tool == "slide":
            dpx = (event.x - self.xref)
            dpy = (event.y - self.yref)
            self.canvas.delete("image")
            self.canvas.create_image(-self.canvas.width + dpx,
                                     -self.canvas.height + dpy, anchor=NW,
                                     image=self.photoimage, tags="image")

    def nomove(self, event):
        if self.tool == "slide":
            self.image_x_abs -= (event.x - self.xref) * numpy.power(2, self.level)
            self.image_y_abs -= (event.y - self.yref) * numpy.power(2, self.level)
            # have to redefine image to store "du rab" for incoming translations
            self.image = self.slide.read_region(location=(self.image_x_abs,
                                                          self.image_y_abs),
                                                level=self.level,
                                                size=(3 * self.canvas.width,
                                                3 * self.canvas.height))
            self.image.putalpha(255)
            self.photoimage = ImageTk.PhotoImage(self.image)
            self.canvas.delete("image")
            self.canvas.create_image(-self.canvas.width, -self.canvas.height,
                                     anchor=NW, image=self.photoimage, tags="image")
            self.canvas.pack()

    def zoom(self):
        # get absolute value of image center
        acx, acy = self.abscenter()

        # reset level
        if self.level > 0:
            self.level -= 1
        self.redraw(acx, acy)

    def dezoom(self):
        # get absolute value of image center
        acx, acy = self.abscenter()

        # reset level
        if self.level < self.slide.level_count - 1:
            self.level += 1
        self.redraw(acx, acy)
