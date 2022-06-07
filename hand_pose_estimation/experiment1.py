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

hand_picture_path='/home/sleekeagle/vuzix/CPR_rate_measuring/hand_pose_estimation/hand_214.jpg'

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
cv2.imwrite('/home/sleekeagle/vuzix/CPR_rate_measuring/hand_pose_estimation/undist.jpg', undist)


#detect keypoints in the hand
mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

IMAGE_FILES = ["/home/sleekeagle/vuzix/CPR_rate_measuring/hand_pose_estimation/undist.jpg"]

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
                        hand_landmarks.landmark[mp_hands.HandLandmark.RING_FINGER_MCP].y*image_height,1]]
        

#get real world coordinates of these points
import physical_hand_measurement
physical_coordinates=physical_hand_measurement.coordinates[0:4]

f=(intrinsic[0][0]+intrinsic[1][1])/2

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

T=np.matmul(np.matmul(np.linalg.inv(Q),W),P).transpose()
invT=np.linalg.inv(T)

out=np.matmul(T.transpose(),physical_coordinates[3])
(out[0]/out[2],out[1]/out[2])

#obtain the vanishing line on the image plane by mapping the ideal line on the object plane 
VLI=np.matmul(np.linalg.inv(T).transpose(),np.array([0,0,1]))
#distance from the origin of the image plane to VLI
DI=abs(VLI[2]/math.sqrt(VLI[0]**2 + VLI[1]**2))
#solve for the dihedral angle theta between the image and the object plane
theta=np.arctan(f/DI)
#obtain the vanishing line in the object plane by mapping the ideal line of the image plane
VLO=np.matmul(T,np.array([0,0,1]))
#compute the point PPO in the object plane (the point where optical axis intersects the object plane)
PPO=np.matmul(np.linalg.inv(T).transpose(),np.array([0,0,1]))
#calculate the distance from PPO to VLO
DO=abs(VLO[0]*PPO[0] + VLO[1]*PPO[1] + VLO[2]*PPO[2])/(PPO[2]*math.sqrt(VLO[0]**2 + VLO[1]**2))
#solve for the plan angle between the normal to VLO and the X axis in the object plane
S=np.arctan(-VLO[1]/VLO[0])
#find the sign of XSGN and YSGN
if((VLO[0]*PPO[0]+VLO[1]*PPO[1]+VLO[2]*PPO[2])/(VLO[0]*PPO[2])<0):
    XSGN=1
else:
    XSGN=-1

if((VLO[0]*PPO[0]+VLO[1]*PPO[1]+VLO[2]*PPO[2])/(VLO[1]*PPO[2])<0):
    YSGN=1
else:
    YSGN=-1

DCP=DO*math.sin(theta)
XCP=XSGN*abs(DCP*math.sin(theta)*math.cos(S))+PPO[0]/PPO[2]
YCP=YSGN*abs(DCP*math.sin(theta)*math.sin(S))+PPO[1]/PPO[2]
ZCP=DCP*math.cos(theta)

theta/math.pi*180
S/math.pi*180

a,b,c=-3.08543363e-04,2.67868644e-04,8.22235871e-01
x=np.linspace(-10,10,100)
y=(-c-a*x)/b
plt.plot(x, y, '-r', label='y=2x+1')


    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    
    

