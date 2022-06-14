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
import numpy as np

cam_param_path='/home/sleekeagle/vuzix/CPR_rate_measuring/cam_calibration/calib_parameters_pixel4a_f1.0.txt'
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
img = cv2.imread(hand_picture_path)
undist = cv2.undistort(img, intrinsic, dist, None, intrinsic)
cv2.imwrite('/home/sleekeagle/vuzix/CPR_rate_measuring/hand_pose_estimation/undist.jpg', undist)


#detect keypoints in the hand
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

IMAGE_FILES = ["/home/sleekeagle/vuzix/CPR_rate_measuring/hand_pose_estimation/hand_distance/hand_images/849.jpg"]

with mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=2,
    min_detection_confidence=0.5) as hands:
  for idx, file in enumerate(IMAGE_FILES):
    # Read an image, flip it around y-axis for correct handedness output (see
    # above).
    image = cv2.flip(cv2.imread(file), 1)
    # Convert the BGR image to RGB before processing.
    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
    # Print handedness and draw hand landmarks on the image.
    print('Handedness:', results.multi_handedness)
    if(results.multi_hand_landmarks):
        image_height, image_width, _ = image.shape
        annotated_image = image.copy()
        for hand_landmarks in results.multi_hand_landmarks:
            mp_drawing.draw_landmarks(
                annotated_image,
                hand_landmarks,
                mp_hands.HAND_CONNECTIONS,
                mp_drawing_styles.get_default_hand_landmarks_style(),
                mp_drawing_styles.get_default_hand_connections_style())
        cv2.imwrite('/home/sleekeagle/vuzix/CPR_rate_measuring/hand_pose_estimation/pose.jpg', cv2.flip(annotated_image, 1))
    
        '''
        We need to extract the 2D coordinates of wrist, knucles of index, middle and ring fingers. 
        their keypoint indexes are,
        0,5,9 and 13
        '''
        img_coordinates = [[hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].x*image_width,
                        hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y*image_height,1],
                       [hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].x*image_width,
                        hand_landmarks.landmark[mp_hands.HandLandmark.INDEX_FINGER_MCP].y*image_height,1],
                       [hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].x*image_width,
                        hand_landmarks.landmark[mp_hands.HandLandmark.MIDDLE_FINGER_MCP].y*image_height,1],
                       [hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].x*image_width,
                        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].y*image_height,1],
                       [hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].x*image_width,
                        hand_landmarks.landmark[mp_hands.HandLandmark.PINKY_MCP].y*image_height,1]]
        

#get real world coordinates of these points
import physical_hand_measurement
import four_point_fischler

physical_coordinates=physical_hand_measurement.coordinates[0:5]

f=(intrinsic[0][0]+intrinsic[1][1])/2

p1=physical_coordinates[0]
p2=physical_coordinates[1]
p3=physical_coordinates[2]
p4=physical_coordinates[3]
p5=physical_coordinates[4]

q1=img_coordinates[0]
q2=img_coordinates[1]
q3=img_coordinates[2]
q4=img_coordinates[3]
q5=img_coordinates[4]
#use 4 point perspective method by Fischler et.al
four_point_fischler.get_camera_pose_Fischler(p1,p2,p3,p4,q1,q2,q3,q4,f,image.shape[0],image.shape[1])


objpts=np.array([p1,p2,p3,p4,q5])
imgpts=np.array([q1[0:2],q2[0:2],q3[0:2],q4[0:2],q5[0:2]])

#from paper Infinitesimal plane-based pose estimation by Collins et.al
cv2.solvePnP(objpts, imgpts, intrinsic, dist, flags=cv2.SOLVEPNP_IPPE)


'''
focal length set at 1.00m
f=3454.58
mm in Z direction
actual distance ||   IPPE   ||  Fischler
204                63.39         329.48           
222                96.62         341.07
252                121.30        332.62
281                180.77        663.53
308                190.29        590.98
400                255.83        142.14
849                582.82         49.75



actual distance diff ||   IPPE   diff  \\ error
0                  0                        
18                33.23                    +15.23
30                24.68                     −5.32
29                59.47                     30.47
27                9.52                      −17.48
92                65.54                     −26.46 
449               326.99                    −122.01

typical distance when CPR around 500 mm (?)
typical error at that distance is around  -26 mm
'''


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

