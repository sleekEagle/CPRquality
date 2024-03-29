import numpy as np
from PIL import Image
import csv
import sys
import cv2
from matplotlib import pyplot as plt

transformed_shape=(720,1280)

def read_csv_data(path):
    with open(path, "r") as filestream:
        for line in filestream:
            currentline = line.split(",")
    vals=[int(item) for item in currentline]
    data=np.array(vals)
    data=np.expand_dims(data,1)
    return data

def read_ptc(file):
    data=read_csv_data(file)
    ind=np.arange(0,data.shape[0])
    x=data[ind%3==0]
    y=data[ind%3==1]
    z=data[ind%3==2]
    return x,y,z

