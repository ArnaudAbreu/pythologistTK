# coding: utf8
"""
Annotation classes
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
import os
import glob
from pythologistTK import view


class AnnotationTab:
    def __init__(self, master, model):

        self.master = master
        self.model = model
        self.isannotation = False
        self.image = None
        self.photoimage = None

        # annotation pannel
        self.annotationPannel = ttk.Frame(self.master, width=200)
        self.annotationPannel.pack(side=LEFT, fill=Y)

        # annotation labeled pannel (inside annotation pannel)
        self.annotationSubPannel = ttk.LabelFrame(self.annotationPannel,
                                                  width=190,
                                                  text="Annotation Browser")
        self.annotationSubPannel.pack(side=TOP, fill=BOTH, expand=YES)

        # scrollable annotation list (inside annotation labeled pannel)
        self.scrollannotations = ttk.Scrollbar(self.annotationSubPannel)
        self.annotationList = Listbox(self.annotationSubPannel, bg="gray25")
        self.annotationList.bind("<<ListboxSelect>>", self.checkAnnotation)
        self.scrollannotations.config(command=self.annotationList.yview)
        self.annotationList.pack(side=LEFT, fill=BOTH, expand=YES)

        # individual annotation pannel
        self.individualPannel = ttk.Frame(self.master, width=600)
        self.individualPannel.pack(side=LEFT, fill=BOTH, expand=YES)

        # annotation rough description pannel
        self.descriptionPannel = ttk.LabelFrame(self.individualPannel,
                                                width=200,
                                                text="Annotation Description")
        self.descriptionPannel.pack(side=LEFT, fill=Y)
        self.propertyList = Listbox(self.descriptionPannel, bg="gray25")
        self.propertyList.pack(side=LEFT, fill=BOTH, expand=YES)

        # annotation thumbnail
        self.patchPannel = ttk.Frame(self.individualPannel)
        self.patchPannel.pack(side=LEFT, fill=BOTH, expand=YES)
        # future "transform pannel" at the bottom
        self.transformPannel = ttk.LabelFrame(self.patchPannel,
                                              height=400,
                                              text="Annotation Transform")
        self.transformPannel.pack(side=BOTTOM, fill=X, expand=YES)
        # viewer is a pretty bad idea or I'll have to modify it deeply
        self.patchView = view.ResizableCanvas(self.patchPannel,
                                              bg="black",
                                              highlightthickness=0)
        self.patchView.pack(side=TOP, fill=BOTH, expand=YES)

    def initAnnot(self):
        namesNcolors = self.model.annotationNames()
        for name in namesNcolors:
            self.annotationList.insert(END, name["name"])
            self.annotationList.itemconfig(END, foreground=name["color"])

    def checkAnnotation(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        color = self.annotationList.itemcget(index, "foreground")
        value = w.get(index)
        detail = self.model.detailedAnnotation(value)
        self.propertyList.delete(0, END)
        for d in detail:
            self.propertyList.insert(END, d)
        bbx, self.image = self.model.imageAnnotation(value)
        self.image.putalpha(255)
        self.photoimage = ImageTk.PhotoImage(self.image)
        self.patchView.delete("all")
        self.patchView.create_image(0,
                                    0,
                                    anchor=NW,
                                    image=self.photoimage,
                                    tags="image")
        self.patchView.create_rectangle(bbx[0], bbx[1], bbx[2], bbx[3], outline=color)
        self.patchView.pack()
