# coding: utf8
"""
Viewer classes
Original author: Arnaud Abreu
"""
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import *
from PIL import Image, ImageTk
from openslide import OpenSlide
import pickle
import numpy
from scipy.misc import imsave


class ResizableCanvas(Canvas):
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


class ViewerTab:
    """
    A simple Viewer class
    """
    def __init__(self, master, model, dim=800):

        self.master = master
        self.model = model
        self.image_x_abs = 0.
        self.image_y_abs = 0.
        self.isSlideOn = False
        self.image = None
        self.photoimage = None
        self.tool = "slide"

        self.xref = 0
        self.yref = 0

        # creation of a frame on the left of the Canvas
        # just to put some buttons and informations
        self.sideFrame = ttk.Frame(self.master, width=100)
        self.sideFrame.pack(side=LEFT, fill=BOTH)

        self.zoomPanel = ttk.LabelFrame(self.sideFrame, width=90,
                                        text="Control Panel")
        self.zoomPanel.pack(side=TOP)

        # image container
        self.canvas = ResizableCanvas(self.master,
                                      width=dim,
                                      height=dim,
                                      highlightthickness=0,
                                      bg="black")
        self.canvas.pack(fill=BOTH, expand=YES)

        # canvas bind events
        self.canvas.bind("<Button-1>", self.dirbutton)
        self.canvas.bind("<B1-Motion>", self.move)
        self.canvas.bind("<ButtonRelease-1>", self.nomove)

        self.buttonzoom = ttk.Button(self.zoomPanel, text="Zoom",
                                     command=self.zoom)
        self.buttondezoom = ttk.Button(self.zoomPanel, text="Dezoom",
                                       command=self.dezoom)

        self.buttonzoom.pack()
        self.buttondezoom.pack()

    def initView(self):
        # done
        """
        A function that create the image in the canvas
        and initialize several variables
        """
        # if there is an image in the canvas, delete it
        self.canvas.delete('all')

        # image creation
        self.image = self.model.initImage()
        self.redraw()
        self.isSlideOn = True

    def redraw(self):
        self.image.putalpha(255)
        self.photoimage = ImageTk.PhotoImage(self.image)
        self.canvas.delete("image")
        self.canvas.create_image(-self.canvas.width,
                                 -self.canvas.height,
                                 anchor=NW,
                                 image=self.photoimage,
                                 tags="image")
        self.canvas.pack()

    def dirbutton(self, event):
        # done
        if self.isSlideOn:
            if self.tool == "slide":
                self.xref = event.x
                self.yref = event.y

    def move(self, event):
        # done
        if self.isSlideOn:
            if self.tool == "slide":
                dpx = (event.x - self.xref)
                dpy = (event.y - self.yref)
                self.canvas.delete("image")
                self.canvas.create_image(-self.canvas.width + dpx,
                                         -self.canvas.height + dpy, anchor=NW,
                                         image=self.photoimage, tags="image")

    def nomove(self, event):
        # done
        if self.isSlideOn:
            if self.tool == "slide":
                self.image = self.model.translateImage(self.xref,
                                                       self.yref,
                                                       event)
                self.redraw()

    def zoom(self):
        if self.isSlideOn:
            # reset level
            self.image = self.model.zoomIn()
            self.redraw()

    def dezoom(self):
        if self.isSlideOn:
            self.image = self.model.zoomOut()
            self.redraw()


class ViewerTabV2(ViewerTab):

    def __init__(self, master, model, dim=800):

        ViewerTab.__init__(self, master, model, dim)

        # variable for spinbox
        self.spinval = IntVar()

        # add a slider
        self.thresholdPanel = ttk.LabelFrame(self.sideFrame, width=90,
                                             text="Threshold Panel")
        self.thresholdPanel.pack(side=TOP)
        self.scale = ttk.Scale(master=self.thresholdPanel, command=self.accept_whole_number_only, orient=VERTICAL, from_=51, to=255)
        self.scale.bind("<ButtonRelease-1>", self.update_annotations)
        self.scale.pack(side=LEFT)

        self.threshspinbox = Spinbox(master=self.thresholdPanel, from_=51, to=255, textvariable=self.spinval, command=self.update, width=10)
        self.threshspinbox.pack(side=LEFT)

    def accept_whole_number_only(self, e=None):
        value = self.scale.get()
        if int(value) != value:
            self.scale.set(round(value))
        self.spinval.set(int(round(value)))
        self.model.thresh = self.spinval.get()

    def update(self, e=None):
        """Updates the scale and spinbox"""
        self.scale.set(self.threshspinbox.get())
        self.model.thresh = self.spinval.get()

    def update_annotations(self, event):
        # can call any function that update annotations in the model
        self.image = self.model.updateImage()
        self.redraw()
