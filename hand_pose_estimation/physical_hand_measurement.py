# -*- coding: utf-8 -*-
"""
Created on Fri Jun  3 17:58:13 2022

@author: Owner
"""
import math

"""  
                       `
                       `          `    
              `        `          `
              `        `          `         `
              `        `          `         `
              `        `          `         `
              `        `          `         ` 
              `     P2(x2,y2)  P3(x3,y3)    `   
  `       P1(x1,0)     #         #      P4(x4,y4)
   `          #        +        +         #
    `          +       +       +        +
     `          +      +      +       +
       `         +     +     +      +
         `        +    +    +     +
           `       +   +   +    +
             `      +  +  +   +
               `     + + +  +  
                      +++ +
                       #   
                      C(0,0)

This is an illustration of a right hand seen from above. 
Define wrist joint as the origin and knuckes of index, middle, ring and little fingers as 
P1,P2,P3 and P4
Let's take CP1 as the X axis. Let y axis be perpendicular to the X axis and away from the body
(so all the Pi will have positive coordinates).
Given distances CP1, P1P2, P1P3 and P1P4
this program gives the cartesian coordinates of P1,P2,P3 and P4
This works for less than 4 fingers as well.

Let the distances CP1,CP2,CP3,CP4 = L1,L2,L3,L4
        distances P1P2,P1P3,P1P4 = D2,D3,D4 

then x1=L1
The cordinates of P2 are derived as follows.
From the equation of circle, 

x = (L1^2 + L2^2 - D2^2)/(2*L1)

Y=|SQRT(L2^2 - X^2)|
    We only keep the positive square root because all the points of interest are in the first quadrent.
"""

L=[93.71,92.95,90.93,88.81]
D=[23.55,44.90,64.52]
coordinates=[]
for i in range(1,len(L)):
    x=(L[0]**2 + L[i]**2 - D[i-1]**2)/(2*L[0])
    y=math.sqrt(L[i]**2-x**2)
    coordinates.append((x,y))

