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
img = cv2.imread(hand_picture_path)
undist = cv2.undistort(img, intrinsic, dist, None, intrinsic)
cv2.imwrite('/home/sleekeagle/vuzix/CPR_rate_measuring/hand_pose_estimation/undist.png', undist)


#detect keypoints in the hand
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

IMAGE_FILES = ["/home/sleekeagle/vuzix/CPR_rate_measuring/hand_pose_estimation/hand_212.jpg"]

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
        cv2.imwrite('/home/sleekeagle/vuzix/CPR_rate_measuring/hand_pose_estimation/pose_212.jpg', cv2.flip(annotated_image, 1))
    
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
                        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].y*image_height,1]]
        
        
#get real world coordinates of these points
import physical_hand_measurement
physical_coordinates=physical_hand_measurement.coordinates[0:4]

#find the homography matrix between the physical and image 
Q=np.array([physical_coordinates[0],physical_coordinates[1],physical_coordinates[2]])
P=np.array([img_coordinates[0],img_coordinates[1],img_coordinates[2]])

V=np.matmul(np.linalg.inv(P).transpose(),img_coordinates[3])
R=np.matmul(np.linalg.inv(Q).transpose(),physical_coordinates[3])

w1=V[0]/R[0]*R[2]/V[2]
w2=V[1]/R[1]*R[2]/V[2]

W=np.array([[w1,0,0],
            [0,w2,0],
            [0,0,1]])

H=np.matmul(np.matmul(np.linalg.inv(Q),W),P)

out=np.matmul(T.transpose(),physical_coordinates[3])
(out[0]/out[2],out[1]/out[2])

'''
H=K*T
K - intrinsic matrix
T - world to camera coordinate system transformation matrix
T=K^(-1)*H
'''

T=np.linalg.inv(intrinsic)*H
trnsl=T[0:3,-1]





    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

