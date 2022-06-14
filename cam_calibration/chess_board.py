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
import json

'''
Calibrate the camera and store the calibration matrix and distortion coefficients in a file
'''

IMG_PATH='/home/sleekeagle/vuzix/CPR_rate_measuring/cam_calibration/pixel4a_f0.3/'
CALIB_PARAM_PATH='/home/sleekeagle/vuzix/CPR_rate_measuring/cam_calibration/calib_parameters_pixel4a_f0.3.txt'

#number of inner corners (where two black squares meet) in short and long dirctions
n_inner_corners_long=9
n_inner_corners_short=6




# termination criteria
criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)

# prepare object points, like (0,0,0), (1,0,0), (2,0,0) ....,(6,5,0)
objp = np.zeros((n_inner_corners_short*n_inner_corners_long,3), np.float32)
objp[:,:2] = np.mgrid[0:n_inner_corners_long,0:n_inner_corners_short].T.reshape(-1,2)

# Arrays to store object points and image points from all the images.
objpoints = [] # 3d point in real world space
imgpoints = [] # 2d points in image plane.
images = glob.glob('*.jpg')

#read all files in the dir
images=os.listdir(IMG_PATH)
images=[path+img for img in images]


for fname in images:
    img = cv.imread(fname)
    #img = cv.resize(img, (403,302))
    gray = cv.cvtColor(img, cv.COLOR_BGR2GRAY)
    # Find the chess board corners
    ret, corners = cv.findChessboardCorners(gray, (n_inner_corners_long,n_inner_corners_short), None)
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

with open(CALIB_PARAM_PATH,'w') as f:
    f.write("intrinsic camera matrix (3x3) \n")
    #write the intrinsic matrix
    for i in range(mtx.shape[0]):
        for j in range(mtx.shape[1]):
            f.write(str(mtx[i][j]))
            if(j!=mtx.shape[1]-1):
                f.write(",")
        f.write("\n")
    f.write("distortion coefficients (1x5) \n")
    #write distortion coefficients
    for i in range(dist.shape[1]):
        f.write(str(dist[0][i]))
        if(i!=dist.shape[1]-1):
            f.write(",")