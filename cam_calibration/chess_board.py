#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 19 15:04:28 2022

@author: sleekeagle
"""

import numpy as np
import cv2 as cv
import glob
import os

# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((6*9,3), np.float32)
objp[:,:2] = np.mgrid[0:9,0:6].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
images = glob.glob('*.jpg')

#read all files in the dir
path='/home/sleekeagle/vuzix/CPR_rate_measuring/cam_calibration/test1_pixel/'
images=os.listdir(path)
images=[path+img for img in images]
fname=images[0]


for fname in images:
    img = cv.imread(fname)
    #img = cv.resize(img, (403,302))
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (9,6), None)
    # If found, add object points, image points (after refining them)
    if ret == True:
        objpoints.append(objp)
        corners2 = cv.cornerSubPix(gray,corners, (11,11), (-1,-1), criteria)
        imgpoints.append(corners)
        print(fname)
        # Draw and display the corners
        #cv.drawChessboardCorners(img, (9,6), corners2, ret)
        #img = cv.resize(img, (960, 540))
        #cv.imshow('img', img)
        #cv.waitKey(0)
#cv.destroyAllWindows()

ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, gray.shape[::-1], None, None)







img_grayscale = cv.imread(path,0)
img_grayscale = cv.resize(img_grayscale, (960, 540))
cv.imshow('graycsale image',img_grayscale)
cv.waitKey(0)
cv.destroyAllWindows()
