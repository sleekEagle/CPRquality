import numpy as np
from matplotlib import pyplot as plt 

file=r"C:\\Users\\lahir\\CPRdata\\acc.csv"
def getIMUdata(file):
    data=np.empty([0,4])
    with open(file, "r") as filestream:
            for line in filestream:
                ts,x,y,z = line.split(",")
                z=z.replace('\n','')
                d=np.array([int(ts),float(x),float(y),float(z)]).reshape(1,4)
                data=np.concatenate((data,d),axis=0)
    return data

def moving_average(x, w):
    return np.convolve(x, np.ones(w), 'valid') / w


'''
read about the coordinate systems of the Azure Kinect camera
https://learn.microsoft.com/en-us/azure/kinect-dk/coordinate-systems



.-.-.-.----->X
| .     .---------------------------.
|   .     .                           .
|     .     .                           . 
V       .     .                           . 
Z         .     .  ------------------------.                         
            .     . -----------------------.      
              .  .  .  
              Y
'''
#returns the direction of gravity wrt to the accelerometer coordinate system
def get_gravity(file):
    imudata=getIMUdata(file)
    #filter with a window of 30 samples (1 seconds at 30fps)
    imu_filt=np.apply_along_axis(moving_average,axis=0,arr=imudata,w=30)
    GRAVITY=-9.8
    gravity_=imu_filt[:,1:]/GRAVITY
    #normalize
    gravity=gravity_/np.expand_dims(gravity_.sum(axis=1),axis=1)
    return imu_filt[:,0],gravity

#transform between acc and RGB coordinste systems given xyz vectors of shape (n,3)
def transform_acc_to_RGB(data):
    data_new=np.empty_like(data)
    data_new[:,0]=-data[:,1]
    data_new[:,1]=data[:,2]
    data_new[:,2]=-data[:,0]
    return data_new

gravity_acc=get_gravity(file)[1]
gravity_rgb=transform_acc_to_RGB(gravity_acc)


