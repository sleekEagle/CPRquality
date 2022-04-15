#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Thu Apr 14 14:43:44 2022

@author: sleekeagle
"""
import serial
import time

f = open("/home/sleekeagle/vuzix/CPR_rate_measuring/VL6188_dist_sensor_characteristic/measure_dist/single_samples_dark_1/1.txt", "w")

ser = serial.Serial('/dev/ttyACM0',115200)
time.sleep(3)
i=0
while(True):
    i+=1
    dist = ser.readline().decode("utf-8")[:-2]
    f.write(dist+'\n')
    if(i==2000):
        break
f.close()



'''
plot mean values
'''
import pandas as pd
import matplotlib.pyplot as plt

file_names=[str(name) for name in list(range(0,19))]
means,stds=[],[]

for fn in file_names:
    try:
        df=pd.read_csv('/home/sleekeagle/vuzix/CPR_rate_measuring/VL6188_dist_sensor_characteristic/measure_dist/single_samples/' +fn+'.txt')
        means.append(df.mean().values[0])
        stds.append(df.std().values[0])
    except:
        print("exception")

plt.scatter(means, stds)
plt.title("Distance vs standard deviation sample size = 2000")
plt.xlabel("Mean Distance mm ")
plt.ylabel("standard deviation mm ")
plt.savefig('/home/sleekeagle/vuzix/CPR_rate_measuring/VL6188_dist_sensor_characteristic/measure_dist/single_samples/std', dpi=300)



df=pd.read_csv('/home/sleekeagle/vuzix/CPR_rate_measuring/VL6188_dist_sensor_characteristic/measure_dist/single_samples/' +fn+'.txt')