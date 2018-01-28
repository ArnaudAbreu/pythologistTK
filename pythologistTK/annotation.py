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


class AnnotationTab:
    def __init__(self, master):

        self.master = master

        # individual annotation pannel
        self.annotationPannel = ttk.Frame(self.master, width=200)
        self.annotationPannel.pack(side=LEFT, fill=Y)

        # annotation labeled frame
        self.annotationSubPannel = ttk.LabelFrame(self.annotationPannel,
                                                  width=190,
                                                  text="Annotation Browser")
        self.annotationSubPannel.pack(side=TOP, fill=BOTH, expand=YES)

        self.scrollannotations = ttk.Scrollbar(self.annotationSubPannel)
        self.annotationList = Listbox(self.annotationSubPannel, bg="gray25")

        self.scrollannotations.config(command=self.annotationList.yview)
        self.annotationList.pack(side=LEFT, fill=Y, expand=YES)
        self.annotations = None

    def open_annotations_file(self, filepath):
        with open(filepath, "rb") as f:
            self.annotations = pickle.load(f)
