#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Jun  6 09:42:06 2022

@author: sleekeagle
"""

import cv2
import mediapipe as mp
import time
import matplotlib.pyplot as plt
import math
import numpy as np


'''
Let's test the method given in the paper "Random Sample Consensus: A Paradigm for Model Fitting with Apphcatlons to Image
            Analysis and Automated Cartography" by Fischler et.al
With a rectangle printed out on a paper

The actual dimentions of the rectangle is a follows:

     Q2(0,108)               Q3(83,108)
        #```````````````````````#
        `                       `
        `                       `
        `                       `
        `                       ` 
        `                       ` 
        `                       `
        `                       ` 
        `                       `
        `                       `
        `                       `
        `                       `  
        #````````````````````````#
      Q1(0,0)                  Q4(83,0)   
      
I printed this out and measured the above dimentions with a ruler.
Then I took several photos of this from various angles and distances. I had to fix the focal length of the 
camera with the OpenCamera app. 
I had found the effective focal length of the camera to be around 3800 from another calibration experiment. 

To convert the image coordinate system to the "normal" system we need to do a modification
                       
   ````````````````````--------------->X
   `                  `
   `                  `   
   `                  `    H (image height)
   `                  `
   `                  `                         <------- X and Y axes of image pixels
   `                  `
   `                  `
   `                  ` 
   ````````````````````
   `    W (image width)
   `
   `
   `
 Y V  
   
X=X
Y=H-Y

so the new coordinate system looks like
Y ^
  `
  `
  `
  `
  `
  ````````````>X

'''

f=3800

q1=[0,0,1]
q2=[0,108,1]
q3=[83,108,1]
q4=[83,0,1]

'''
I took photos when the angle between the actual rectangle plane and the mobile phone (hence the camea)
is at approximately different angles;
around 90, 60 and 0
I measures these angles by eye. So only approximate. 
'''
#around 90
p1=[3794,3000-2331,1]
p2=[3216,3000-2093,1]
p3=[3212,3000-1289,1]
p4=[3775,3000-1157,1]

#around 60
p1=[2949,3000-2190,1]
p2=[2042,3000-2145,1]
p3=[2002,3000-1378,1]
p4=[2865,3000-1189,1]


#around 0
p1=[2174,3000-1737,1]
p2=[1002,3000-1656,1]
p3=[1030,3000-740,1]
p4=[2227,3000-761,1]



Q=np.array([q1,q2,q3])
P=np.array([p1,p2,p3])

V=np.matmul(np.linalg.inv(P).transpose(),p4)
R=np.matmul(np.linalg.inv(Q).transpose(),q4)

w1=V[0]/R[0]*R[2]/V[2]
w2=V[1]/R[1]*R[2]/V[2]

W=np.array([[w1,0,0],
            [0,w2,0],
            [0,0,1]])

T=np.matmul(np.matmul(np.linalg.inv(Q),W),P).transpose()
invT=np.linalg.inv(T)

#obtain the vanishing line on the image plane by mapping the ideal line on the object plane 
VLI=np.matmul(invT.transpose(),np.array([0,0,1]))
#distance from the origin of the image plane to VLI
DI=VLI[2]/math.sqrt(VLI[0]**2 + VLI[1]**2)
#solve for the dihedral angle theta between the image and the object plane
if(DI<0):
    theta=np.arctan(1/abs(DI))+math.pi/2
else:
    theta=np.arctan(f/DI)
theta/math.pi*180


#obtain the vanishing line in the object plane by mapping the ideal line of the image plane
VLO=np.matmul(T.transpose(),np.array([0,0,1]))
#compute the point PPO in the object plane (the point where optical axis intersects the object plane)
PPO=np.matmul(invT,np.array([0,0,1]))
#calculate the distance from PPO to VLO
DO=(VLO[0]*PPO[0] + VLO[1]*PPO[1] + VLO[2]*PPO[2])/(PPO[2]*math.sqrt(VLO[0]**2 + VLO[1]**2))
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

'''
results 
in degrees

measured angle | calculated angle
90                   90.02
60                   76.75
0                    14.04

I would say the errors are within plausible human error bounds
'''



'''
I took photos with varying distances between the camera (image plane) 
and the rectangle plane (object plane)

'''

#furthest
p1=[3148,3000-1612,1]
p2=[2708,3000-1637,1]
p3=[2684,3000-1324,1]
p4=[3123,3000-1279,1]

#medium
p1=[2639,3000-1840,1]
p2=[1880,3000-1854,1]
p3=[1862,3000-1287,1]
p4=[2612,3000-1227,1]

#closest
p1=[2608,3000-2252,1]
p2=[906,3000-2227,1]
p3=[852,3000-938,1]
p4=[2535,3000-786,1]


Q=np.array([q1,q2,q3])
P=np.array([p1,p2,p3])

V=np.matmul(np.linalg.inv(P).transpose(),p4)
R=np.matmul(np.linalg.inv(Q).transpose(),q4)

w1=V[0]/R[0]*R[2]/V[2]
w2=V[1]/R[1]*R[2]/V[2]

W=np.array([[w1,0,0],
            [0,w2,0],
            [0,0,1]])

T=np.matmul(np.matmul(np.linalg.inv(Q),W),P).transpose()
invT=np.linalg.inv(T)

#obtain the vanishing line on the image plane by mapping the ideal line on the object plane 
VLI=np.matmul(invT.transpose(),np.array([0,0,1]))
#distance from the origin of the image plane to VLI
DI=VLI[2]/math.sqrt(VLI[0]**2 + VLI[1]**2)
#solve for the dihedral angle theta between the image and the object plane
if(DI<0):
    theta=np.arctan(1/abs(DI))+math.pi/2
else:
    theta=np.arctan(f/DI)
theta/math.pi*180



#obtain the vanishing line in the object plane by mapping the ideal line of the image plane
VLO=np.matmul(T.transpose(),np.array([0,0,1]))
#compute the point PPO in the object plane (the point where optical axis intersects the object plane)
PPO=np.matmul(invT,np.array([0,0,1]))
[PPO[0]/PPO[2],PPO[1]/PPO[2]]
#calculate the distance from PPO to VLO
DO=(VLO[0]*PPO[0] + VLO[1]*PPO[1] + VLO[2]*PPO[2])/(PPO[2]*math.sqrt(VLO[0]**2 + VLO[1]**2))
#solve for the plan angle between the normal to VLO and the X axis in the object plane
S=np.arctan(-VLO[1]/VLO[0])
S/math.pi*180

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


'''
results in mm (because I measured the rectangle dimentions in mm)

setting    |   calculated distance (mm)

farthest           1523
medium              703
closest             286

It seems like the obtained distances are coherent with the settings.
Absolute accuracy is yet to be determined by more reliable experiments. 
'''


'''
Measuring and comparing with actual distances
3 acutual distances were used 
735mm,590mm and 560mm
The image of the rectangle was used
'''
#focal length fixed at 1m
#focal length in pixels (obtained from calibration)
f=(3460+3448)/2

#735mm ground truth
p1=[1346,3000-1728,1]
p2=[885,3000-1736,1]
p3=[881,3000-1381,1]
p4=[1341,3000-1372,1]

#590mm ground truth
p1=[1830,3000-1890,1]
p2=[1249,3000-1920,1]
p3=[1231,3000-1476,1]
p4=[1809,3000-1447,1]

#560mm ground truth
p1=[1959,3000-2088,1]
p2=[1360,3000-2100,1]
p3=[1349,3000-1640,1]
p4=[1947,3000-1624,1]




Q=np.array([q1,q2,q3])
P=np.array([p1,p2,p3])

V=np.matmul(np.linalg.inv(P).transpose(),p4)
R=np.matmul(np.linalg.inv(Q).transpose(),q4)

w1=V[0]/R[0]*R[2]/V[2]
w2=V[1]/R[1]*R[2]/V[2]

W=np.array([[w1,0,0],
            [0,w2,0],
            [0,0,1]])

T=np.matmul(np.matmul(np.linalg.inv(Q),W),P).transpose()
invT=np.linalg.inv(T)

#obtain the vanishing line on the image plane by mapping the ideal line on the object plane 
VLI=np.matmul(invT.transpose(),np.array([0,0,1]))
#distance from the origin of the image plane to VLI
DI=VLI[2]/math.sqrt(VLI[0]**2 + VLI[1]**2)
#solve for the dihedral angle theta between the image and the object plane
if(DI<0):
    theta=np.arctan(1/abs(DI))+math.pi/2
else:
    theta=np.arctan(f/DI)
theta/math.pi*180


#obtain the vanishing line in the object plane by mapping the ideal line of the image plane
VLO=np.matmul(T.transpose(),np.array([0,0,1]))
#compute the point PPO in the object plane (the point where optical axis intersects the object plane)
PPO=np.matmul(invT,np.array([0,0,1]))
#calculate the distance from PPO to VLO
DO=(VLO[0]*PPO[0] + VLO[1]*PPO[1] + VLO[2]*PPO[2])/(PPO[2]*math.sqrt(VLO[0]**2 + VLO[1]**2))
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


q1=[0,0,1]
q2=[0,108,1]
q3=[83,108,1]
q4=[83,0,1]




imgpts=np.array([(1959,2088),
          (1360,2100),
          (1349,1640),
          (1947,1624)], dtype="double")


imgpts=np.array([(1830,1890),
          (1249,1920),
          (1231,1476),
          (1809,1447)], dtype="double")

imgpts=np.array([(1346,1728),
          (885,1736),
          (881,1381),
          (1341,1372)], dtype="double")


objpts=np.array([(0.0,0.0,0),
                 (0.0,108.0,0),
                 (83.0,108.0,0),
                 (83.0,0.0,0)])


imgpts = np.array([(359, 391),     # Nose tip
                         (399, 561),     # Chin
                         (337, 297),     # Left eye left corner
                         (513, 301),     # Right eye right corne
                         ], dtype="double")

objpts = np.array([(0.0, 0.0, 1),             # Nose tip
                         (0.0, -330.0, 1),        # Chin
                         (-225.0, 170.0, 1),     # Left eye left corner
                         (225.0, 170.0, 1),      # Right eye right corne
                         ])



cammtx=np.array([[3460.98,0,1710.21],
                 [0,3448.178,1542.68],
                 [0,0,1]])
distCoeffs=np.array([-0.12890835939029746,0.5631854505539805,-0.020464215414698363,-0.009766070275441416,-1.1781219140070995])

cv2.solvePnP(objpts, imgpts, cammtx, distCoeffs, flags=cv2.SOLVEPNP_IPPE)



















