# coding: utf8

from skimage.io import imread
from skimage.measure import label
from openslide import OpenSlide
import numpy
import sys
from skimage.morphology import dilation
import os
import pickle

slidename = str(sys.argv[1])

probapath = str(sys.argv[2])

offsetx = 0
offsety = 0

slide = OpenSlide(slidename)

probaimage = imread(probapath)

if probaimage.ndim == 3:
    probaimage = probaimage[:, :, 1]

posy, posx = numpy.where(probaimage > 84)

posx *= 500

posx += (offsetx * 4)

posy *= 500

posy += (offsety * 4)

dico = dict()

# brown contours version
# for k in range(len(posx)):
#     image = numpy.array(slide.read_region(location=(posx[k], posy[k]), level=0, size=(500, 500)))[:, :, 0:3]
#     brown = image[:, :, 0].astype(float) / (1. + image[:, :, 2].astype(float))
#     brown = brown > 1.3
#     d = dilation(brown)
#     inv = numpy.logical_not(brown)
#     c = numpy.logical_and(inv, d)
#     c[0, :] = 1
#     c[:, 0] = 1
#     c[-1, :] = 1
#     c[:, -1] = 1
#     y, x = numpy.where(c > 0)
#     y += posy[k]
#     x += posx[k]
#     dico["brown_" + str(k + 1)] = {'coords': [(x[c], y[c]) for c in range(len(x))],
#                                    'color': "magenta",
#                                    'id': k + 1,
#                                    'class': 'spe'}

# only box version
for k in range(len(posx)):
    image = numpy.zeros((500, 500), numpy.uint8)
    c[0, :] = 1
    c[:, 0] = 1
    c[-1, :] = 1
    c[:, -1] = 1
    y, x = numpy.where(c > 0)
    y += posy[k]
    x += posx[k]
    dico["brown_" + str(k + 1)] = {'coords': [(x[c], y[c]) for c in range(len(x))],
                                   'color': 'magenta',
                                   'id': k + 1,
                                   'class': 'spe'}


name = slidename.split('.')[0]

n = 1

if os.path.exists(name + ".annot"):
    while os.path.exists(name + "_" + str(n) + ".annot"):
        n += 1

    with open(name + "_" + str(n) + ".annot", "wb") as f:
        pickle.dump(dico, f)

else:
    with open(name + ".annot", "wb") as f:
        pickle.dump(dico, f)
