#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Dec  7 15:06:42 2021

@author: sleekeagle
"""
import cv2
import mediapipe as mp
import time
import matplotlib.pyplot as plt
import math

y_vals=[]

mp_drawing = mp.solutions.drawing_utils
mp_drawing_styles = mp.solutions.drawing_styles
mp_hands = mp.solutions.hands

'/home/sleekeagle/vuzix/CPR_rate_measuring/experiment_2022_03_30/trimmed.mp4'

'/home/sleekeagle/vuzix/CPR_rate_measuring/experiment_2022_03_30/detection.avi'

def get_hand_coordinates(video_in,video_out):
    #open video 
    cap = cv2.VideoCapture(video_in)
    #get the frame rate of the video
    fps=int(cap.get(cv2.CAP_PROP_FPS))
    
    if (cap.isOpened()== False):
        print("Error opening video stream or file")
        
        
    #for a video stream
    n_empty=0
    n_frames=0
    start = time.time()
    img_array=[]
    cnt=0
    with mp_hands.Hands(
        model_complexity=0,
        max_num_hands=2,
        min_detection_confidence=0.5,
        min_tracking_confidence=0.5) as hands:
      while cap.isOpened():
        success, image = cap.read()
        if success:
            height, width, layers = image.shape
            size = (width,height)
            #create output file once
            if(cnt==0):
                #output video file
                out = cv2.VideoWriter(video_out,
                                      cv2.VideoWriter_fourcc(*'DIVX'), 30, size)
            cnt+=1
            if(cnt%100==0):
                print(str(cnt) +" frames procesed")
        else:
            y_vals.append(math.nan)
            n_empty+=1
            if(n_empty>5):
                print('too many empty frames. quitting...')
                break
            print("Ignoring empty camera frame.")
            # If loading a video, use 'break' instead of 'continue'.
            continue
        n_empty=0
        n_frames+=1
        # To improve performance, optionally mark the image as not writeable to
        # pass by reference.
        image.flags.writeable = False
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        results = hands.process(image)
        #end = time.time()
        #print(end - start)
        #print(n_frames)
    
        # Draw the hand annotations on the image.
        
        image.flags.writeable = True
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
        if results.multi_hand_landmarks:
            for hand_landmarks in results.multi_hand_landmarks:
                y_vals.append(hand_landmarks.landmark[mp_hands.HandLandmark.WRIST].y)
                mp_drawing.draw_landmarks(
                    image,
                    hand_landmarks,
                    mp_hands.HAND_CONNECTIONS,
                    mp_drawing_styles.get_default_hand_landmarks_style(),
                    mp_drawing_styles.get_default_hand_connections_style())
            out.write(image)
        else:
            y_vals.append(math.nan)
            # Flip the image horizontally for a selfie-view display.
            #cv2.imshow('MediaPipe Hands', cv2.flip(image, 1))
            #img_array.append(image)
 
    out.release()        
    cap.release()
    
    return y_vals