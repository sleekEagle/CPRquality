#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Apr  3 11:15:00 2022

@author: sleekeagle
"""

import pandas as pd
import matplotlib.pyplot as plt
import hand_pose
import numpy as np
from scipy.signal import find_peaks

#time in ms between adjecent samples
sample_time=10

df = pd.read_csv('/home/sleekeagle/vuzix/CPR_rate_measuring/experiment_2022_03_30/G7NZCJ00817029H-CPR-Test-Lahiru-Adult-Right-Testing-2022-03-30-12-58-58.csv',
                 sep=',')

df.columns=['ts','sensor','accuracy','x','y','z']
start_time=df['ts'].iloc[0]
end_time=df['ts'].iloc[-1]

new_df=pd.DataFrame(range(start_time,end_time,sample_time))
new_df.columns=['ts']

mer=pd.merge(right=df,left=new_df,how='outer',on='ts')
mer=mer.sort_values(by=['ts']).reset_index()
inter=mer.interpolate()
inter['ts']=pd.to_datetime(inter['ts'],unit='ms')
inter.reset_index()
inter=inter.drop(['index'],axis=1)
inter=inter.set_index('ts')


#required sample rate in Hz
req_sample_rate=30
resampled=inter.resample('33.33ms').mean()
resampled['seconds']=(resampled.index-resampled.index[0]).total_seconds()
resampled=resampled.set_index('seconds')

#get detected wrist joint coordinates
y_vals=hand_pose.get_hand_coordinates('/home/sleekeagle/vuzix/CPR_rate_measuring/experiment_2022_03_30/trimmed.mp4',
                                      '/home/sleekeagle/vuzix/CPR_rate_measuring/experiment_2022_03_30/detection.avi')
y_vals=y_vals[:len(resampled)]
y_vals_norm=(y_vals-np.mean(y_vals))/np.std(y_vals)


acc_z=resampled['z'].values
acc_z_norm=(acc_z-np.mean(acc_z))/(np.max(acc_z)-np.min(acc_z))


#plot z axis of the smart watch based acc data
fig, ax = plt.subplots()
ax.plot(resampled.index,acc_z,label='smartwatch acceleration m/s^2 - z axis')
plt.xlabel('time in seconds')
plt.title("Smartwatch based acceleration - z axis")
plt.ylabel("m/s^2")
#plt.show()
plt.savefig("/home/sleekeagle/vuzix/CPR_rate_measuring/experiment_2022_03_30/plots/acc.png",dpi=300)

#plot y position of the wrist position of hand
fig, ax = plt.subplots()
ax.plot(resampled.index,y_vals)
plt.xlabel('time in seconds')
plt.title("Normalized wrist position of left hand- wrist y axis")
plt.ylabel("Normalized distance")
#plt.show()
plt.savefig("/home/sleekeagle/vuzix/CPR_rate_measuring/experiment_2022_03_30/plots/hand_y.png",dpi=300)


fig, ax = plt.subplots()
ax.plot(resampled.index,acc_z_norm,label='Normalized smartwatch acceleration - z axis')
ax.plot(resampled.index,y_vals,label='Normalized wrist position - y axis')
legend = ax.legend(loc='upper right', shadow=True, fontsize='large')
plt.xlabel('time in seconds')
plt.ylim([-0.5, 1.8])
plt.savefig("/home/sleekeagle/vuzix/CPR_rate_measuring/experiment_2022_03_30/plots/hand_acc_combined_norm.png",dpi=300)

'''
detect the CPR rate from the data
'''
#from hand position (y axis - writst)
start_ind=750
end_ind=1750

wrist_data=y_vals[750:1750]
plt.plot(wrist_data)
#plot
fig, ax = plt.subplots()
ax.plot(resampled.index[750:1750],wrist_data)
plt.xlabel('time in seconds')
plt.title("Normalized wrist position of left hand wrist during CPR")
plt.savefig("/home/sleekeagle/vuzix/CPR_rate_measuring/experiment_2022_03_30/plots/CPR_hand.png",dpi=300)

#get running mean 
mean=np.convolve(wrist_data, np.ones(50)/50, mode='valid')
mean=np.pad(mean,(len(wrist_data)-len(mean),0),'edge')

plt.plot(wrist_data)
plt.plot(mean)

#normalize by removing mean 
wrist_data_norm=wrist_data-mean

#detect peaks for hand detection
peaks, _ = find_peaks(wrist_data_norm, height=0)
peak_ind=resampled.index[750:1750][peaks]

fig, ax = plt.subplots()
ax.plot(resampled.index[750:1750],wrist_data_norm)
ax.plot(peak_ind,wrist_data_norm[peaks],"x")
plt.title("Peak detection for the normalized left hand wrist position during CPR")
plt.xlabel('time in seconds')
plt.savefig("/home/sleekeagle/vuzix/CPR_rate_measuring/experiment_2022_03_30/plots/peak_detection_hand.png",dpi=300)



#detect peaks for acc data
cpr_acc=acc_z_norm[750:1750]
#get running mean
mean=np.convolve(cpr_acc, np.ones(50)/50, mode='valid')
mean=np.pad(mean,(len(cpr_acc)-len(mean),0),'edge')

#remove mean
cpr_acc_no_mean=cpr_acc-mean

#smooth
cpr_smooth=np.convolve(cpr_acc_no_mean, np.ones(50)/50, mode='valid')
cpr_smooth=np.pad(cpr_smooth,(len(resampled.index[750:1750])-len(cpr_smooth),0),'edge')


peaks, _ = find_peaks(cpr_smooth, height=0.005)
peak_ind=resampled.index[750:1750][peaks]
len(peaks)

#plot detected peaks
fig, ax = plt.subplots()
ax.plot(resampled.index[750:1750],cpr_smooth)
ax.plot(peak_ind,cpr_smooth[peaks],"x")
plt.title("Peak detection for the normalized, smoothed \n smartwatch based Z acceleration")
plt.xlabel('time in seconds')
plt.savefig("/home/sleekeagle/vuzix/CPR_rate_measuring/experiment_2022_03_30/plots/peak_detection_acc.png",dpi=300)



#detect zero crossing
zero_crossings = np.where(np.diff(np.sign(wrist_data_norm)))[0]
zero_crossing_vals=wrist_data_norm[zero_crossings]
zero_crsing_ind=resampled.index[750:1750][zero_crossings]

fig, ax = plt.subplots()
ax.plot(resampled.index[750:1750],wrist_data_norm,label='')
ax.plot(zero_crsing_ind,zero_crossing_vals,marker='o',
        markersize=3,
        linestyle = 'None',
        label='')
plt.title("Zero crossing detection for the left hand wrist during CPR")
plt.xlabel('time in seconds')
plt.ylabel("Normalized wrist position")
plt.savefig("/home/sleekeagle/vuzix/CPR_rate_measuring/experiment_2022_03_30/plots/Sero_crossing_detection_hand.png",dpi=300)

plt.show()


plt.savefig("/home/sleekeagle/vuzix/CPR_rate_measuring/experiment_2022_03_30/plots/fff.png",dpi=300)



#from z acc of smartwatch based data
len(np.where(np.diff(np.sign(acc_z_norm)))[0])





