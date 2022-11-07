import os
import sys
import csv

current = os.path.dirname(os.path.realpath(__file__))
parent = os.path.dirname(current)
sys.path.append(parent)

import azurekinect.read_azure_img as azureimg
import azurekinect.read_azure_imu as azureimu
import cv2
import mediapipe as mp
import numpy as np
import subprocess
import Arduino.readdistsensor

#extract images
out = subprocess.run('ffmpeg -i C:\\Users\\lahir\\CPRdata\\vid.mkv -map 0:0  -vsync 0 C:\\Users\\lahir\\CPRdata\\outputs\\rgb%04d.png', shell=True)

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

#read rgb images from a directory
rgbpath="C:\\Users\\lahir\\CPRdata\\data2\\outputs\\"
dir_list = os.listdir(rgbpath)
dir_list.sort()
imgs=[rgbpath+file for file in dir_list if (file.split('.')[-1]=='png')]

#open video file to write
image = cv2.imread(imgs[0])
image_height, image_width, _ = image.shape
fourcc = cv2.VideoWriter_fourcc('M','J','P','G')
video = cv2.VideoWriter('C:\\Users\\lahir\\CPRdata\\data2\\outputs\\annotated\\vid.avi', fourcc, 30, (image_width, image_height))

wrist_coords=[]
with mp_hands.Hands(
    static_image_mode=True,
    max_num_hands=1,
    min_detection_confidence=0.5) as hands:
  for idx, file in enumerate(imgs):
    # Read an image, flip it around y-axis for correct handedness output (see
    # above).
    image = cv2.imread(file)
    image_height, image_width, _ = image.shape
    # Convert the BGR image to RGB before processing.
    results = hands.process(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Print handedness and draw hand landmarks on the image.
    print('Handedness:', results.multi_handedness)
    if not results.multi_hand_landmarks:
        wrist_coords.append(())
        continue
    annotated_image = image.copy()
    for hand_landmarks in results.multi_hand_landmarks:
        x = results.multi_hand_landmarks[0].landmark[0].x
        y = results.multi_hand_landmarks[0].landmark[0].y
        z = results.multi_hand_landmarks[0].landmark[0].z
        relative_x = int(x * image_width)
        relative_y = int(y * image_height)
        wrist_coords.append((relative_x,relative_y))
        print("Wrist coordinate: X,Y", relative_x,relative_y)
        annoimg=cv2.circle(image, (relative_x, relative_y), radius=30, color=(0, 255, 0), thickness=3)
        label = "({0},{1})".format(relative_x, relative_y)
        annoimg=cv2.putText(image,label, (relative_x+30,relative_y), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0,255,0),2)
        cv2.imwrite('C:\\Users\\lahir\\CPRdata\\data2\\outputs\\annotated\\' + str(idx) + '.png', annoimg)
        video.write(annoimg)


from matplotlib import pyplot as plt
transformed_shape=(720,1280)  

#read timestamps
tsfile='C:\\Users\\lahir\\CPRdata\\data2\\ts.txt'
def read_ts(file):
    ts=[]
    with open(file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=' ', quotechar='|')
        for row in spamreader:
            try:
                splt= (', '.join(row)).split()
                ts_=int(splt[0])
                ts.append(ts_)
            except Exception as e:
                print(str(e))
    return ts

allts=read_ts(tsfile)
wrist_coords_xyz=np.empty([0, 3])
valid_ind=[]
ptcpasth="C:\\Users\\lahir\\CPRdata\\data2\\outputs\\transformed\\"
WRISTWINDOW=5
for i,wrist in enumerate(wrist_coords):
    if(not(len(wrist)==2)):
        continue
    else:
        ptcfile=ptcpasth+str(i).zfill(3)+".ptc"
        x,y,z=azureimg.read_ptc(ptcfile)
        wrist_x=x.reshape(transformed_shape)[wrist[1]-WRISTWINDOW:wrist[1]+WRISTWINDOW,wrist[0]-WRISTWINDOW:wrist[0]+WRISTWINDOW].mean()
        wrist_y=y.reshape(transformed_shape)[wrist[1]-WRISTWINDOW:wrist[1]+WRISTWINDOW,wrist[0]-WRISTWINDOW:wrist[0]+WRISTWINDOW].mean()
        wrist_z=z.reshape(transformed_shape)[wrist[1]-WRISTWINDOW:wrist[1]+WRISTWINDOW,wrist[0]-WRISTWINDOW:wrist[0]+WRISTWINDOW].mean()
        #print(wrist_x,wrist_y,wrist_z)
        if(abs(wrist_x)>1 and abs(wrist_x)<10000 and abs(wrist_y)>1 and abs(wrist_y)<10000 and abs(wrist_z)>1 and abs(wrist_z)<10000):
            wrist_coords_xyz=np.concatenate((wrist_coords_xyz,np.array([[wrist_x,wrist_y,wrist_z]])),axis=0)
            valid_ind.append(i)
        print(ptcfile)

#get gravity direction (what vector is down ?)
accfile=r"C:\\Users\\lahir\\CPRdata\\data2\\acc.csv"
ts,gravity=azureimu.get_gravity(accfile)
#get gravity wrt rgb camera coordinate frame
gravity=azureimu.transform_acc_to_RGB(gravity)
#lets assume azure kinect was still the whole time. So we can simply get the mean direction of gravity
gravity=np.mean(gravity,axis=0)
gravity=gravity/np.sum(gravity)
projections=[]
for i in range(wrist_coords_xyz.shape[0]):
    projections.append(np.dot(wrist_coords_xyz[i,:],gravity))

outfile='C:\\Users\\lahir\\CPRdata\\data2\\outputs\\movement.txt'
header = ['ts', 'dist']
with open(outfile, 'w', encoding='UTF8') as f:
    writer = csv.writer(f)
    writer.writerow(header)
    for i,ind in enumerate(valid_ind):
        data=[]
        data.append(str(allts[ind]))
        data.append(str(projections[i]))
        writer.writerow(data)

plt.plot(projections)
plt.title('Wrist position perpendicular to the floor in mm')
plt.xlabel('frame number')
plt.savefig('C:\\Users\\lahir\\CPRdata\\outputs\\wristpos.png')
plt.show()


#read distance from dist sensor

depthts,depthvals=Arduino.readdistsensor.get_depthdata(r'C:\Users\lahir\Documents\CPR Quality Data\CoolTerm Capture 2022-10-20 15-15-25.txt')
#manually check the valid range of the depths (where actual CPR is taking place)
valid_depthvals=depthvals[1260:5575]
#read the visually calcualted depths from file
file=r'C:\Users\lahir\CPRdata\data2\outputs\movement.txt'
def read_depth(file):
    vals=[]
    with open(file, newline='') as csvfile:
        spamreader = csv.reader(csvfile, delimiter=',', quotechar='|')
        for row in spamreader:
            try:
                splt= (', '.join(row)).split()
                val_=float(splt[1])
                vals.append(val_)
            except Exception as e:
                print(str(e))
    return vals


visual_depth=read_depth(file)
valid_visualdepth=visual_depth[7:]
#remove outliers
valid_visualdepth=np.array(valid_visualdepth)
outlier=np.abs((valid_visualdepth-np.mean(valid_visualdepth))/np.std(valid_visualdepth))<1.5
valid_visualdepth=valid_visualdepth[outlier]
visual_zeromean=valid_visualdepth-np.mean(valid_visualdepth)


kernel_size = 5
kernel = np.ones(kernel_size) / kernel_size
depth_conv = np.convolve(valid_depthvals, kernel, mode='same')

from scipy import signal
depth_resampled = signal.resample(depth_conv, 534)
depth_resampled_zeromean=depth_resampled-np.mean(depth_resampled)



plt.plot(depth_resampled_zeromean)
plt.plot(visual_zeromean)
plt.xlabel('Sample number')
plt.ylabel('Distance from mean in mm')
plt.legend(['VL6180 sensor', 'Kinect depth+hand detection'])
plt.savefig(r'C:\Users\lahir\CPRdata\data2\outputs\bothdist.png',dpi=500)
plt.show()




























