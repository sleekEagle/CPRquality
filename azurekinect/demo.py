import azurekinect.read_azure_img as azureimg
import azurekinect.read_azure_imu as azureimu
import os
import cv2
import mediapipe as mp
import numpy as np

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

#read rgb images from a directory
rgbpath="C:\\Users\\lahir\\CPRdata\\outputs\\"
dir_list = os.listdir(rgbpath)
dir_list.sort()
imgs=[rgbpath+file for file in dir_list if (file.split('.')[-1]=='png')]

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
        cv2.imwrite('C:\\Users\\lahir\\CPRdata\\outputs\\annotated\\' + str(idx) + '.png', annoimg)


from matplotlib import pyplot as plt
transformed_shape=(720,1280)   

wrist_coords_xyz=np.empty([0, 3])
valid_ind=[]
ptcpasth="C:\\Users\\lahir\\CPRdata\\outputs\\transformed\\"
WRISTWINDOW=10
for i,wrist in enumerate(wrist_coords):
    if(not(len(wrist)==2)):
        continue
    else:
        ptcfile=ptcpasth+str(i)+".ptc"
        x,y,z=azureimg.read_ptc(ptcfile)
        wrist_x=x.reshape(transformed_shape)[wrist[1]-WRISTWINDOW:wrist[1]+WRISTWINDOW,wrist[0]-WRISTWINDOW:wrist[0]+WRISTWINDOW].mean()
        wrist_y=y.reshape(transformed_shape)[wrist[1]-WRISTWINDOW:wrist[1]+WRISTWINDOW,wrist[0]-WRISTWINDOW:wrist[0]+WRISTWINDOW].mean()
        wrist_z=z.reshape(transformed_shape)[wrist[1]-WRISTWINDOW:wrist[1]+WRISTWINDOW,wrist[0]-WRISTWINDOW:wrist[0]+WRISTWINDOW].mean()
        if(abs(wrist_x)>1 and abs(wrist_x)<10000 and abs(wrist_y)>1 and abs(wrist_y)<10000 and abs(wrist_z)>1 and abs(wrist_z)<10000):
            wrist_coords_xyz=np.concatenate((wrist_coords_xyz,np.array([[wrist_x,wrist_y,wrist_z]])),axis=0)
            valid_ind.append(i)
        print(ptcfile)

#get gravity direction (what vector is down ?)
accfile=r"C:\\Users\\lahir\\CPRdata\\acc.csv"
ts,gravity=azureimu.get_gravity(accfile)
#get gravity wrt rgb camera coordinate frame
gravity=azureimu.transform_acc_to_RGB(gravity)
#lets assume azure kinect was still the whole time. So we can simply get the mean direction of gravity
gravity=np.mean(gravity,axis=0)












