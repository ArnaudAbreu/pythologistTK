# coding: utf8
"""
Viewer classes
Original author: Arnaud Abreu
"""
from tkinter import *
from tkinter import ttk
from tkinter.filedialog import *
import PIL
from PIL import ImageTk, Image
from PIL.Image import *
from PIL.Image import BOX, LINEAR, NEAREST, EXTENT, fromarray
import numpy 

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
        self.isSuperposed = False
        self.image = None
        self.cmap = None
        self.initWidthCmap = 0
        self.initHeightCmap = 0
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

    def initViewPng(self):
        # done
        """
        A function that create the image in the canvas
        and initialize several variables
        """
        # if there is an image in the canvas, delete it
        self.canvas.delete('all')

        # image creation
        self.cmap = self.model.initImagePng()
        self.redrawPng()
        self.isCmapOn = True

    def initViewSuperposed(self):
        # done
        """
        A function that create the image in the canvas
        and initialize several variables
        """
        # if there is an image in the canvas, delete it
        print("im in superposition mode")
        self.canvas.delete('all')

        # image creation
        self.image = self.model.initImage()
        self.cmap = self.model.initImagePng()
        self.initWidthCmap = self.cmap.size[0]
        self.initHeightCmap = self.cmap.size[0]
        self.isSuperposed = True
        self.isSlideOn = True
        self.redrawSuperposed()
        

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

    def my_resize(self,size): #Not better than PIL.Image.transform or resize method
        
        needed_y , needed_x = size
        size_new_image = max([needed_x,needed_y])
        new_image = PIL.Image.new('RGBA',(size_new_image,size_new_image))
        n = numpy.array(new_image)
        factor = (2**self.model.level)
        pixel_size = 1

        for key in self.model.positions.keys():
            if key != 'size_x' and key != 'size_y': 
                xo = int( (key[0] *598) / factor)
                yo = int( (key[1] *598) /factor)


            if self.model.level > 7:
                pixel_size = 1

            if self.model.level == 7:              
                pixel_size = 4

            if self.model.level == 6:              
                pixel_size = 9

            if self.model.level == 5:              
                pixel_size = 18

            if self.model.level == 4:            
                pixel_size = 37

            if self.model.level == 3:               
                pixel_size = 74

            elif self.model.level == 2:              
                pixel_size = 149

            elif self.model.level == 1:              
                pixel_size = 299

            elif self.model.level == 0:
                pixel_size = 598   

            for i in range(pixel_size):
                for j in range(pixel_size):
                    x_good = xo + i
                    y_good = yo + j
                    if x_good > needed_x:
                        x_good = 0
                    if y_good > needed_y:
                        y_good = 0
                    #print("i want ", x_good,y_good)
                    n[x_good,y_good] = self.model.positions[key]

        new_image = PIL.Image.fromarray(n)
        print("cmap size : ",new_image.size,"| slide size :", needed_x,needed_y, "| zoom lvl :", self.model.level, "| pixel size :", pixel_size)
        return new_image


    def redrawSuperposed(self):
        self.image.putalpha(255)

        n = numpy.array(self.image)
        x, y = numpy.where(n[:, :, 0] > 0)
        #print(x,y)
        min_x = int(min(x))
        min_y = int(min(y))
        max_x = int(max(x))
        max_y = int(max(y))
        dx = max_x - min_x
        dy = max_y - min_y
        size = (dy,dx)
        #print("Size cmap ",self.cmap.size,"Zoom factor ",self.model.level)

        #self.cmap = self.cmap.transform(size,EXTENT,(0,0)+self.cmap.size)
        self.cmap = self.my_resize((dx,dy))
        self.image.paste(self.cmap,(min_y,min_x),self.cmap)
        #print(self.image.size)

        self.photoimage = ImageTk.PhotoImage(self.image)
        #self.cmap = ImageTk.PhotoImage(self.cmap)
        #self.photoimage = self.photoimage.paste(self.cmap)
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

        if self.isSuperposed:
            if self.tool == "slide":
                self.image = self.model.translateImage(self.xref,
                                                       self.yref,
                                                       event)
                self.redrawSuperposed()

        if self.isSlideOn and self.isSuperposed == False:
            if self.tool == "slide":
                self.image = self.model.translateImage(self.xref,
                                                       self.yref,
                                                       event)
                self.redraw()

    def zoom(self):
        if self.isSuperposed:
            self.image = self.model.zoomIn()
            self.redrawSuperposed()

        if self.isSlideOn and self.isSuperposed == False:
            # reset level
            self.image = self.model.zoomIn()
            self.redraw()

    def dezoom(self):
        if self.isSuperposed:
            self.image = self.model.zoomOut()
            self.redrawSuperposed()

        if self.isSlideOn and self.isSuperposed == False:
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
