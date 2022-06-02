# -*- coding: utf-8 -*-
"""
Created on Tue May 31 20:45:00 2022

@author: Owner
"""


import numpy as np
import math
'''
From the paper "Random Sample Consensus: A Paradigm for Model Fitting with Apphcatlons to Image
            Analysis and Automated Cartography" by Fischler et.al
'''
A = np.array([[6, 1, 1],
              [4, -2, 5],
              [2, 8, 7]])

A = np.array([[1, 0, 0],
              [0, 1, 0],
              [0, 2, 0]])


#define 
p1=[-0.071263,0.029665,1]
p2=[-0.053033,-0.006379,1]
p3=[-0.014063,0.061579,1]
p4=[0.080120,-0.030305,1]

q1=[-30,80,1]
q2=[-100,-20,1]
q3=[140,50,1]
q4=[-40,-240,1]

Q=np.array([q1,q2,q3])
P=np.array([p1,p2,p3])

V=np.matmul(np.linalg.inv(P).transpose(),p4)
R=np.matmul(np.linalg.inv(Q).transpose(),q4)

w1=V[0]/R[0]*R[2]/V[2]
w2=V[1]/R[1]*R[2]/V[2]

W=np.array([[w1,0,0],
            [0,w2,0],
            [0,0,1]])

T=np.matmul(np.matmul(np.linalg.inv(Q),W),P)


#obtain the vanishing line on the image plane by mapping the ideal line on the object plane 
VLI=np.matmul(np.linalg.inv(T),np.array([0,0,1]))
#distance from the origin of the image plane to VLI
DI=abs(VLI[2]/math.sqrt(VLI[0]**2 + VLI[1]**2))
