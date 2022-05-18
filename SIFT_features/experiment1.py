#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed May 18 10:39:02 2022

@author: sleekeagle
"""

import cv2 
import matplotlib.pyplot as plt
%matplotlib inline


PXL_20220518_143216693.MP.jpg

#reading image
img1 = cv2.imread('/home/sleekeagle/vuzix/CPR_rate_measuring/SIFT_features/images/PXL_20220518_143215729.MP.jpg')  
gray1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)

#keypoints
sift = cv2.xfeatures2d.SIFT_create()
keypoints_1, descriptors_1 = sift.detectAndCompute(img1,None)

img_1 = cv2.drawKeypoints(gray1,keypoints_1,img1)
plt.imshow(img_1)
cv2.imwrite('/home/sleekeagle/vuzix/CPR_rate_measuring/SIFT_features/images/keypts.jpg',img_1)

#*********************************************

#two images
# read images
img1 = cv2.imread('/home/sleekeagle/vuzix/CPR_rate_measuring/SIFT_features/images/PXL_20220518_143214775.MP.jpg')  
img2 = cv2.imread('/home/sleekeagle/vuzix/CPR_rate_measuring/SIFT_features/images/PXL_20220518_143215729.MP.jpg') 

img1 = cv2.cvtColor(img1, cv2.COLOR_BGR2GRAY)
img2 = cv2.cvtColor(img2, cv2.COLOR_BGR2GRAY)

#sift
sift = cv2.xfeatures2d.SIFT_create()

keypoints_1, descriptors_1 = sift.detectAndCompute(img1,None)
keypoints_2, descriptors_2 = sift.detectAndCompute(img2,None)

#feature matching
bf = cv2.BFMatcher(cv2.NORM_L1, crossCheck=True)

matches = bf.match(descriptors_1,descriptors_2)
matches = sorted(matches, key = lambda x:x.distance)

img3 = cv2.drawMatches(img1, keypoints_1, img2, keypoints_2, matches[:50], img2, flags=2)
plt.imshow(img3),plt.show()
