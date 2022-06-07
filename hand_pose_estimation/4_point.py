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
f=0.3048
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

def get_camera_pose(p1,p2,p3,p4,q1,q2,q3,q4,f):

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
    DI=abs(VLI[2]/math.sqrt(VLI[0]**2 + VLI[1]**2))
    #solve for the dihedral angle theta between the image and the object plane
    theta=np.arctan(f/DI)
    #obtain the vanishing line in the object plane by mapping the ideal line of the image plane
    VLO=np.matmul(T,np.array([0,0,1]))
    #compute the point PPO in the object plane (the point where optical axis intersects the object plane)
    PPO=np.matmul(np.linalg.inv(T).transpose(),np.array([0,0,1]))
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
    
    return XCP,YCP,ZCP
    


