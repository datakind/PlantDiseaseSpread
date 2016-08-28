# -*- coding: utf-8 -*-
"""
Created on Sat Aug 27 17:18:01 2016

@author: colinheye
"""

# import the necessary packages
import numpy as np
import argparse
import glob
#import cv2
from PIL import Image
import matplotlib.pyplot as plt
from skimage.filters import sobel, roberts
from skimage import feature
from skimage import measure
from skimage import morphology
from collections import Counter
import operator
from scipy import ndimage

lowClip = 10 # Percent of original image
highClip = 30

#%%
im = Image.open("../Data/17/43375-17.png")
imarr = np.asarray(im)
#edge_robe = feature.canny(imarr)
edge_canny = feature.canny(imarr, sigma=2.0)


#%%
plt.imshow(edge_canny, cmap='Greys') #,  interpolation='nearest') #tight_layout()

#%%
plt.figure(figsize=(9,9))
dilat2 = morphology.binary_dilation(edge_canny)
dilat = morphology.binary_dilation(dilat2)
plt.imshow(dilat)

#%%
mask=(dilat==0)*1
plt.imshow(mask)

#%%
label_image = measure.label(mask)
plt.imshow(-label_image)
plt.colorbar()

#%%
pix = label_image.ravel()

#%%
rgns = Counter(pix)
sorted_rgns = np.asarray(sorted(rgns.items(), key=operator.itemgetter(1)))

#%%
lowerLimit = (lowClip/100)**2.0*np.shape(imarr)[0]*np.shape(imarr)[1]
upperLimit = (highClip/100)**2.0*np.shape(imarr)[0]*np.shape(imarr)[1]
mask2 = ((sorted_rgns[:,1] > lowerLimit) & (sorted_rgns[:,1] < upperLimit))
zones = sorted_rgns[mask2][:,0]
    
#%%
#def get_obj(arr):
#    new=[]
#    for i in range(len(arr)):
#        strx=str(i)
#        new.append(strx[5::])
#    return new

for z in zones:        
    chk2 = (label_image==z)*1
    bboxes = ndimage.measurements.find_objects(chk2)
    #lims = get_obj(bboxes)
    chk3 = chk2[bboxes[0][0].start:bboxes[0][0].stop, bboxes[0][1].start:bboxes[0][1].stop]
    chk3pad = np.lib.pad(chk3,(1,1),'constant',constant_values=0)
    edgeIm = sobel(chk3pad.astype('float64'))
    edgeIm[edgeIm > 0] = 1
    plt.figure(figsize=(7,7))
    plt.imshow(edgeIm)
#    plt.imshow(chk3)
    plt.show()
    print(sum(sum(edgeIm))/np.prod(np.asarray(np.shape(chk3))))
    print(sum(sum(edgeIm))/(2*(sum(np.asarray(np.shape(chk3))))))
    
    