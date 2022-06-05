#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jun  5 12:28:23 2022

@author: sleekeagle
"""

import cv2
import mediapipe as mp
import time
import matplotlib.pyplot as plt
import math

hand_picture_path='/home/sleekeagle/vuzix/CPR_rate_measuring/hand_pose_estimation/hand_211.jpg'

cam_param_path='/home/sleekeagle/vuzix/CPR_rate_measuring/cam_calibration/calib_parameters.txt'
#read intrinsic matrix and distortion coefficients
values=[]
with open(cam_param_path) as f:
    lines=f.readlines()
    lines=[line.rstrip() for line in lines]
    intrinsic=lines[1:4]
    val=[item.split(",") for item in intrinsic]
    for ar in val:
        tmp_ar=[]
        for item in ar:
            tmp_ar.append(float(item))
        values.append(tmp_ar)
    intrinsic=np.array(values)
    
    dist=lines[-1]
    dist=np.array([float(item) for item in dist.split(",")])
    

#undistort image
img = cv.imread(hand_picture_path)
undist = cv2.undistort(img, intrinsic, dist, None, intrinsic)
cv.imwrite('/home/sleekeagle/vuzix/CPR_rate_measuring/hand_pose_estimation/undist.png', undist)





