"""
Model part of the interface.

Classes.
"""

from tkinter import *
from tkinter import ttk
from tkinter.filedialog import *
from tkinter import messagebox
from pythologistTK import application, processes
from PIL import ImageDraw,ImageTk, Image
from openslide import OpenSlide
import pickle
import numpy
from numpy import savetxt, save
from inspect import getmembers, isfunction
from skimage.io import imread
import pickle

def zoomFactors(slide):
    zoomdict = dict()
    absdim = slide.level_dimensions[0][0]
    level = 0
    for leveldims in slide.level_dimensions:
        xdim = leveldims[0]
        zoomdict[level] = int(absdim / xdim)
        level += 1
    return zoomdict


def getbox(xcenter, ycenter, size=500):
    """
    A function to compute coordinates of a bounding box.

    Arguments:
        - xcenter: int, x position of the center of the box.
        - ycenter: int, y position of the center of the box.
        - size: int, size of the side of the box.

    Returns:
        - box: list of tuple of int, (x, y) coordinates of the sides of the box.
    """
    xo = xcenter - int(size / 2)
    yo = ycenter - int(size / 2)
    xe = xcenter + int(size / 2)
    ye = ycenter + int(size / 2)
    horizonhaut = [(x, yo) for x in range(xo, xe)]
    horizonbas = [(x, ye) for x in range(xo, xe)]
    verticalgauche = [(xo, y) for y in range(yo, ye)]
    verticaldroite = [(xe, y) for y in range(yo, ye)]
    box = horizonbas + horizonhaut + verticaldroite + verticalgauche
    return box


class Model:
    def __init__(self, master):

        # master is the tkinter main application
        self.master = master
        self.slidefilepath = None
        self.annotationfilepath = None


################################################################################
        # Menu creation
################################################################################
        # Menu bar
        self.menubar = Menu(self.master)

        # File Menu
        self.file_menu = Menu(self.menubar)
        self.file_menu.add_command(label="Open Image",
                                   command=self.open_files)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        # link the menu to the app
        self.master.config(menu=self.menubar)


################################################################################
        # processable objects
################################################################################
        self.slide = None
        self.image_x_abs = 0.
        self.image_y_abs = 0.
        self.annotations = None


################################################################################
        # View : sub-application (TabApplication)
################################################################################
        # master of the view application is the main tkinter application,
        # not the model itself
        self.view = application.TabApplication(self.master, self)


################################################################################
        # functions for image streaming
################################################################################

    def open_files(self):
        # get path of the slide
        self.slidefilepath = askopenfilename(title="open image",
                                             filetypes=[('mrxs files', '.mrxs'),
                                                        ('aperio files', '.svs'),
                                                        ('hamamatsu files', '.ndpi'),
                                                        ('hamamatsu2 files', '.vms'),
                                                        ('hamamatsu3 files', '.vmu'),
                                                        ('leica files', '.scn'),
                                                        ('tiff files', '.tiff'),
                                                        ('sakura files', '.svslide'),
                                                        ('ventana files', '.bif'),
                                                        ('tif files', '.tif'),
                                                        ('all files', '.*'),('png files', '.png')])
        # print(type(self.slidefilepath))
        if self.slidefilepath:
            # create the slide object
            #self.slide = OpenSlide(self.slidefilepath)
            print("open file : ", self.slidefilepath)
            print("HELLO")
            # get path of the annotation file
            self.annotationfilepath = self.slidefilepath.split(".")[0] + ".annot"
            # create the annotation object
            self.annotations = None
            if os.path.exists(self.annotationfilepath):
                self.view.annotapp.isannotation = True
                with open(self.annotationfilepath, "rb") as f:
                    self.annotations = pickle.load(f)
            else:
                self.annotations = dict()
            self.view.viewapp.initView()
            self.view.annotapp.initAnnot()
            self.zoomfactors = zoomFactors(self.slide)


    def initImage(self):
        # define current level of observation to lowest level (highest on pyramid)
        canvasheight = self.view.viewapp.canvas.height
        canvaswidth = self.view.viewapp.canvas.width
        self.level = self.slide.level_count - 1

        # create an image low resolution to find ROI in current level
        im = numpy.array(self.slide.read_region(location=(0, 0),
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
        ci1 = ci - int(canvasheight + (canvasheight / 2))
        cj1 = cj - int(canvaswidth + (canvaswidth / 2))
        self.cmapy = -ci1
        self.cmapx = -cj1
        # image absolute position in slide
        self.image_y_abs = ci1 * self.zoomfactors[self.level]
        self.image_x_abs = cj1 * self.zoomfactors[self.level]
        print('Absolute y position:' + str(self.image_y_abs))
        print('Absolute x position:' + str(self.image_x_abs))

        # image creation
        image = self.slide.read_region(location=(self.image_x_abs,
                                                 self.image_y_abs),
                                       level=self.level,
                                       size=(3*canvaswidth,
                                             3*canvasheight))
        print("I think I read level: ", self.level)
        return image

    def initImagePng(self):
        cmap = self.cmap_png
        return cmap

    def translateImage(self, xref, yref, event):
        canvasheight = self.view.viewapp.canvas.height
        canvaswidth = self.view.viewapp.canvas.width
        self.image_x_abs -= (event.x - xref) * self.zoomfactors[self.level]
        self.image_y_abs -= (event.y - yref) * self.zoomfactors[self.level]
        self.cmapy -= (event.y - yref)
        self.cmapx -= (event.x - xref)
        # have to redefine image to store "du rab" for incoming translations
        image = self.slide.read_region(location=(self.image_x_abs,
                                                 self.image_y_abs),
                                       level=self.level,
                                       size=(3 * canvaswidth,
                                             3 * canvasheight))
        return image

    def zoomImage(self, x, y):
        canvasheight = self.view.viewapp.canvas.height
        canvaswidth = self.view.viewapp.canvas.width
        self.image_x_abs = x - int(canvaswidth + (canvaswidth / 2)) * self.zoomfactors[self.level]
        self.image_y_abs = y - int(canvasheight + (canvasheight / 2)) * self.zoomfactors[self.level]

        # get image position in canvas at new level
        image = self.slide.read_region(location=(self.image_x_abs,
                                                 self.image_y_abs),
                                       level=self.level,
                                       size=(3 * canvaswidth,
                                             3 * canvasheight))

        return image

    def abscenter(self):
        canvasheight = self.view.viewapp.canvas.height
        canvaswidth = self.view.viewapp.canvas.width
        abscenterx = self.image_x_abs + int(canvaswidth + (canvaswidth / 2)) * self.zoomfactors[self.level]
        abscentery = self.image_y_abs + int(canvasheight + (canvasheight / 2)) * self.zoomfactors[self.level]
        return abscenterx, abscentery

    def canvasBbox(self):
        canvasheight = self.view.viewapp.canvas.height
        canvaswidth = self.view.viewapp.canvas.width
        absHLcornerx = self.image_x_abs + canvaswidth * self.zoomfactors[self.level]
        absHLcornery = self.image_y_abs + canvasheight * self.zoomfactors[self.level]
        absLRcornerx = self.image_x_abs + canvaswidth * self.zoomfactors[self.level] * 2
        absLRcornery = self.image_y_abs + canvasheight * self.zoomfactors[self.level] * 2
        return absHLcornerx, absHLcornery, absLRcornerx, absLRcornery

    def zoomIn(self):
        # get absolute center
        absx, absy = self.abscenter()
        # reset level
        if self.level > 0:
            self.level -= 1
        # recompute image
        image = self.zoomImage(absx, absy)
        return image

    def zoomOut(self):
        # get absolute center
        absx, absy = self.abscenter()
        # reset level
        if self.level < self.slide.level_count - 1:
            self.level += 1
        # recompute image
        image = self.zoomImage(absx, absy)
        return image


################################################################################
        # functions for annotations processing
################################################################################
    def annotationNames(self):
        namesNcolors = []
        for key in self.annotations.keys():
            namesNcolors.append({"name": key, "color": self.annotations[key]["color"]})
        return namesNcolors

    def annotationNamesByPropertyVal(self, val):
        namesNcolors = []
        for key in self.annotations.keys():
            if val in self.annotations[key].values():
                namesNcolors.append({"name": key, "color": self.annotations[key]["color"]})
        return namesNcolors

    def annotationUniqueProperties(self):
        properties = []
        for key in self.annotations.keys():
            annotation = self.annotations[key]
            for k in annotation.keys():
                if str(k) == "class" or str(k) == "color":
                    if annotation[k] not in properties:
                        properties.append(annotation[k])
        return properties

    def detailedAnnotation(self, name):
        detail = []
        for key in self.annotations[name]:
            detail.append(str(key) + " : " + str(self.annotations[name][key]))
        return detail

    def imageAnnotation(self, name):
        coords = self.annotations[name]["coords"]
        sizex = self.view.annotapp.patchView.width
        sizey = self.view.annotapp.patchView.height
        i = numpy.array([c[1] for c in coords])
        j = numpy.array([c[0] for c in coords])
        imin = i.min()
        jmin = j.min()
        imax = i.max()
        jmax = j.max()
        imiddle = int(float(imax - imin) / 2)
        jmiddle = int(float(jmax - jmin) / 2)
        di = imax - imin
        dj = jmax - jmin
        k = 2
        while (float(di) / numpy.power(2, k)) > sizey and (float(dj) / numpy.power(2, k)) > sizex:
            k += 1
        absoriginx = jmin + int(float(dj) / 2) - (int(float(sizex) / 2) * (2 ** k))
        absoriginy = imin + int(float(di) / 2) - (int(float(sizey) / 2) * (2 ** k))
        image = self.slide.read_region(location=(absoriginx, absoriginy),
                                       level=k,
                                       size=(sizex, sizey))
        bbx = (int(float(sizex) / 2 - ((float(dj) / 2) / (2 ** k))),
               int(float(sizey) / 2 - ((float(di) / 2) / (2 ** k))),
               int(float(sizex) / 2 - ((float(dj) / 2) / (2 ** k)) + (dj / (2 ** k))),
               int(float(sizey) / 2 - ((float(di) / 2) / (2 ** k)) + (di / (2 ** k))))
        return bbx, image

    def findProcesses(self):
        functions_list = [o[0] for o in getmembers(processes) if isfunction(o[1]) and "process" in o[0]]
        return functions_list

    def runProcess(self, processname, progressbar):
        functions_list = [o for o in getmembers(processes) if isfunction(o[1]) and "process" in o[0]]
        process = None
        for f in functions_list:
            if f[0] == processname:
                process = f[1]
                break
        if process is not None:
            process(self.annotations, self.slide, progressbar)
        if bool(self.annotations):
            self.view.annotapp.isannotation = True

    def saveAnnotations(self):
        if self.annotationfilepath is not None:
            with open(self.annotationfilepath, "wb") as f:
                pickle.dump(self.annotations, f)


class ModelV2(Model):

    def __init__(self, master):

        # master is the tkinter main application
        self.master = master
        self.slidefilepath = None
        self.annotationfile = None
        self.annotations = None
        self.thresh = 84


################################################################################
        # Menu creation
################################################################################
        # Menu bar
        self.menubar = Menu(self.master)

        # File Menu
        self.file_menu = Menu(self.menubar)
        self.file_menu.add_command(label="Open Image",
                                   command=self.open_files)
        self.file_menu.add_command(label="Superpose Cmap",
                                   command=self.superpose_cmap)
        self.menubar.add_cascade(label="File", menu=self.file_menu)

        # link the menu to the app
        self.master.config(menu=self.menubar)


################################################################################
        # processable objects
################################################################################
        self.slide = None
        self.cmap_png = None
        self.cmapy = 0
        self.cmapx = 0
        self.positions = {}
        self.image_x_abs = 0.
        self.image_y_abs = 0.


################################################################################
        # View : sub-application (TabApplication)
################################################################################
        # master of the view application is the main tkinter application,
        # not the model itself
        self.view = application.TabApplicationV2(self.master, self)


################################################################################
        # functions for image streaming
################################################################################

    def open_files(self):
        # get path of the slide
        self.slidefilepath = askopenfilename(title="open image",
                                             filetypes=[('mrxs files', '.mrxs'),
                                                        ('aperio files', '.svs'),
                                                        ('hamamatsu files', '.ndpi'),
                                                        ('hamamatsu2 files', '.vms'),
                                                        ('hamamatsu3 files', '.vmu'),
                                                        ('leica files', '.scn'),
                                                        ('tiff files', '.tiff'),
                                                        ('sakura files', '.svslide'),
                                                        ('ventana files', '.bif'),
                                                        ('tif files', '.tif'),
                                                        ('all files', '.*')])
        # print(type(self.slidefilepath))
        if self.slidefilepath:
            # create the slide object
            self.slide = OpenSlide(self.slidefilepath)
            print("open file : ", self.slidefilepath)
            self.zoomfactors = zoomFactors(self.slide)
        self.view.viewapp.initView()

    def superpose_cmap(self):
        self.pngpath = askopenfilename(title="open cmap",
                                             filetypes=[('png files', '.png'),('all files', '.*')])
        if self.pngpath:
            if messagebox.askyesno(message="Is this a FISH color map?"):
                self.view.viewapp.isFISH = True
            else:
                self.view.viewapp.isFISH = False
            # create the cmap object
            self.cmap_png = Image.open(self.pngpath)
            self.cmap_png.putalpha(100)
            size_x , size_y = self.cmap_png.size
            n = numpy.array(self.cmap_png)
            for i in range(n.shape[0]):
                for j in range(n.shape[1]):
                    if n[i,j,0] == 0 and n[i,j,1] == 0 and n[i,j,2] == 0:
                        n[i,j,3] = 0
                    self.positions[(i,j)] = n[i,j]
            self.positions['size_x'] = size_x
            self.positions['size_y'] = size_y

            with open('positions_in_cmap.p','wb') as fp:
                pickle.dump(self.positions,fp)

            self.cmap_png = Image.fromarray(n)
            print("Taille cmap : ",self.cmap_png.size)
            #self.cmap_png = imread(self.pngpath)
            print("open png file : ", self.pngpath)
        self.view.viewapp.initViewSuperposed()

        return 0


    def open_annotation_files(self, filename):

        self.annotationfile = filename
        if self.annotationfile:
            if '.annot' in self.annotationfile:
                with open(self.annotationfile, 'rb') as f:
                    self.annotations = pickle.load(f)
                    self.view.annotapp.isannotation = True
                    self.boxes = dict()
                    for key, value in self.annotations.items():
                        coords = value['coords']
                        xmin = min([c[0] for c in coords])
                        ymin = min([c[1] for c in coords])
                        xmax = max([c[0] for c in coords])
                        ymax = max([c[1] for c in coords])
                        self.boxes[key] = [(xmin, ymin), (xmin, ymax), (xmax, ymin), (xmax, ymax)]

    def translateImage(self, xref, yref, event):
        canvasheight = self.view.viewapp.canvas.height
        canvaswidth = self.view.viewapp.canvas.width
        self.image_x_abs -= (event.x - xref) * self.zoomfactors[self.level]
        self.image_y_abs -= (event.y - yref) * self.zoomfactors[self.level]
        self.cmapy += (event.y - yref)
        self.cmapx += (event.x - xref)
        # have to redefine image to store "du rab" for incoming translations
        image = self.slide.read_region(location=(self.image_x_abs,
                                                 self.image_y_abs),
                                       level=self.level,
                                       size=(3 * canvaswidth,
                                             3 * canvasheight))

        if self.annotations is not None:
            image = self.drawAnnotation(image)

        return image

    def zoomImage(self, x, y):
        canvasheight = self.view.viewapp.canvas.height
        canvaswidth = self.view.viewapp.canvas.width
        self.image_x_abs = x - int(canvaswidth + (canvaswidth / 2)) * self.zoomfactors[self.level]
        self.image_y_abs = y - int(canvasheight + (canvasheight / 2)) * self.zoomfactors[self.level]
        self.cmapy = - int((self.image_y_abs / self.zoomfactors[self.level]))
        self.cmapx = - int((self.image_x_abs / self.zoomfactors[self.level]))
        # get image position in canvas at new level
        image = self.slide.read_region(location=(self.image_x_abs,
                                                 self.image_y_abs),
                                       level=self.level,
                                       size=(3 * canvaswidth,
                                             3 * canvasheight))
        # draw annotation if possible
        if self.annotations is not None:
            image = self.drawAnnotation(image)
        return image

    def active_color(self, color):
        c = self.master.winfo_rgb(color)
        r = c[0] / 65535 * 255
        g = c[1] / 65535 * 255
        b = c[2] / 65535 * 255
        return (round(r), round(g), round(b))

    def drawAnnotation(self, image):
        """
        image is a pillow image out of slide.read_region().
        """
        if isinstance(self.annotations, dict):
            # first define the absolute size of the bounding box
            absheight = (3 * self.view.viewapp.canvas.height) * self.zoomfactors[self.level]
            abswidth = (3 * self.view.viewapp.canvas.width) * self.zoomfactors[self.level]

            # then find all annotations that belongs to the box
            # assertion: I have annotations at level 0...
            visible = []
            for key, box in self.boxes.items():
                x = numpy.array([c[0] for c in box])
                y = numpy.array([c[1] for c in box])
                xinside = numpy.logical_and(x < self.image_x_abs + abswidth, x > self.image_x_abs)
                yinside = numpy.logical_and(y < self.image_y_abs + absheight, y > self.image_y_abs)
                both = numpy.logical_and(xinside, yinside)
                if both.any():
                    visible.append(key)

            for key in visible:
                coords = self.annotations[key]['coords']
                x = numpy.array([c[0] for c in coords], dtype=float)
                y = numpy.array([c[1] for c in coords], dtype=float)
                x -= self.image_x_abs
                y -= self.image_y_abs
                x /= self.zoomfactors[self.level]
                y /= self.zoomfactors[self.level]
                x = x.astype(int)
                y = y.astype(int)
                relcoords = set([(x[k], y[k]) for k in range(len(x))])
                # whatever happen, if the region is too small, should be able to put a flag...
                # let's put it at x[0], y[0]
                c0 = (x[0], y[0])
                if 'flags' in self.annotations.keys() and self.annotations['flag'] is True:
                    if c0[0] >= 0 and c0[0] < 3 * self.view.viewapp.canvas.width and c0[1] >= 0 and c0[1] < 3 * self.view.viewapp.canvas.height:
                        draw = ImageDraw.Draw(image)
                        draw.rectangle(((c0[0], c0[1]), (c0[0] + 50, c0[1] + 20)), fill=str(self.annotations[key]['color']))
                        draw.text((c0[0], c0[1]), str(self.annotations[key]['id']))
                if self.annotations[key]['display'] == 'point':
                    for c in relcoords:
                        if c[0] >= 0 and c[0] < 3 * self.view.viewapp.canvas.width and c[1] >= 0 and c[1] < 3 * self.view.viewapp.canvas.height:
                            image.putpixel(c, self.active_color(self.annotations[key]['color']))
                elif self.annotations[key]['display'] == 'box':
                    if 'proba' in self.annotations[key].keys():
                        if self.annotations[key]['proba'] > self.thresh:
                            for center in relcoords:
                                box = getbox(center[0], center[1], size=int(500 / self.zoomfactors[self.level]))
                                for c in box:
                                    if c[0] >= 0 and c[0] < 3 * self.view.viewapp.canvas.width and c[1] >= 0 and c[1] < 3 * self.view.viewapp.canvas.height:
                                        image.putpixel(c, self.active_color(self.annotations[key]['color']))
                    else:
                        for center in relcoords:
                            box = getbox(center[0], center[1], size=int(500 / self.zoomfactors[self.level]))
                            for c in box:
                                if c[0] >= 0 and c[0] < 3 * self.view.viewapp.canvas.width and c[1] >= 0 and c[1] < 3 * self.view.viewapp.canvas.height:
                                    image.putpixel(c, self.active_color(self.annotations[key]['color']))

            return image

    def updateImage(self):
        canvasheight = self.view.viewapp.canvas.height
        canvaswidth = self.view.viewapp.canvas.width

        # get image position in canvas at new level
        image = self.slide.read_region(location=(self.image_x_abs,
                                                 self.image_y_abs),
                                       level=self.level,
                                       size=(3 * canvaswidth,
                                             3 * canvasheight))
        # draw annotation if possible
        if self.annotations is not None:
            image = self.drawAnnotation(image)
        return image
