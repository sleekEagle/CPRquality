'''
code was mostly coppied form 
https://temugeb.github.io/opencv/python/2021/02/02/stereo-camera-calibration-and-triangulation.html
by 
Temuge Batpurev
'''

import cv2 as cv
import glob
import numpy as np
from numpy import savetxt

rows = 6 #number of checkerboard rows.
columns = 9 #number of checkerboard columns.


def calibrate_camera(images_folder):
    images_names = sorted(glob.glob(images_folder))
    images = []
    for imname in images_names:
        im = cv.imread(imname, 1)
        images.append(im)
 
    #criteria used by checkerboard pattern detector.
    #Change this if the code can't find the checkerboard
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 30, 0.001)
    world_scaling = 1. #change this to the real world square size. Or not.
 
    #coordinates of squares in the checkerboard world space
    objp = np.zeros((rows*columns,3), np.float32)
    objp[:,:2] = np.mgrid[0:rows,0:columns].T.reshape(-1,2)
    objp = world_scaling* objp
 
    #frame dimensions. Frames should be the same size.
    width = images[0].shape[1]
    height = images[0].shape[0]
 
    #Pixel coordinates of checkerboards
    imgpoints = [] # 2d points in image plane.
 
    #coordinates of the checkerboard in checkerboard world space.
    objpoints = [] # 3d point in real world space
 
    detected=0
    for frame in images:
        gray = cv.cvtColor(frame, cv.COLOR_BGR2GRAY)
 
        #find the checkerboard
        ret, corners = cv.findChessboardCorners(gray, (rows, columns), None)
 
        if ret == True:
            detected+=1
            #Convolution size used to improve corner detection. Don't make this too large.
            conv_size = (11, 11)
 
            #opencv can attempt to improve the checkerboard coordinates
            corners = cv.cornerSubPix(gray, corners, conv_size, (-1, -1), criteria)
            cv.drawChessboardCorners(frame, (rows,columns), corners, ret)
            cv.imshow('img', frame)
            k = cv.waitKey(500)
 
            objpoints.append(objp)
            imgpoints.append(corners)
 
 
 
    ret, mtx, dist, rvecs, tvecs = cv.calibrateCamera(objpoints, imgpoints, (width, height), None, None)
    print('rmse:', ret)
    print('camera matrix:\n', mtx)
    print('distortion coeffs:', dist)
    print('Rs:\n', rvecs)
    print('Ts:\n', tvecs)
 
    return mtx, dist,detected


def stereo_calibrate(mtx1, dist1, mtx2, dist2, cam1dir,cam2dir):
    #read the synched frames
    cam1_images_names = glob.glob(cam1dir)
    cam2_images_names = glob.glob(cam2dir)
    cam1_images_names = sorted(cam1_images_names)
    cam2_images_names = sorted(cam2_images_names)
 
    c1_images = []
    c2_images = []
    for im1, im2 in zip(cam1_images_names, cam2_images_names):
        _im = cv.imread(im1, 1)
        c1_images.append(_im)
 
        _im = cv.imread(im2, 1)
        c2_images.append(_im)
 
    #change this if stereo calibration not good.
    criteria = (cv.TERM_CRITERIA_EPS + cv.TERM_CRITERIA_MAX_ITER, 100, 0.0001)
    world_scaling = 1. #change this to the real world square size. Or not.
 
    #coordinates of squares in the checkerboard world space
    objp = np.zeros((rows*columns,3), np.float32)
    objp[:,:2] = np.mgrid[0:rows,0:columns].T.reshape(-1,2)
    objp = world_scaling* objp
 
    #frame dimensions. Frames should be the same size.
    width = c1_images[0].shape[1]
    height = c1_images[0].shape[0]
 
    #Pixel coordinates of checkerboards
    imgpoints_left = [] # 2d points in image plane.
    imgpoints_right = []
 
    #coordinates of the checkerboard in checkerboard world space.
    objpoints = [] # 3d point in real world space
    ngoodpairs=0
    for frame1, frame2 in zip(c1_images, c2_images):
        gray1 = cv.cvtColor(frame1, cv.COLOR_BGR2GRAY)
        gray2 = cv.cvtColor(frame2, cv.COLOR_BGR2GRAY)
        c_ret1, corners1 = cv.findChessboardCorners(gray1, (rows, columns), None)
        c_ret2, corners2 = cv.findChessboardCorners(gray2, (rows, columns), None)
 
        if c_ret1 == True and c_ret2 == True:
            ngoodpairs+=1
            corners1 = cv.cornerSubPix(gray1, corners1, (11, 11), (-1, -1), criteria)
            corners2 = cv.cornerSubPix(gray2, corners2, (11, 11), (-1, -1), criteria)
 
            cv.drawChessboardCorners(frame1, (rows, columns), corners1, c_ret1)
            cv.imshow('img', frame1)
 
            cv.drawChessboardCorners(frame2, (rows, columns), corners2, c_ret2)
            cv.imshow('img2', frame2)
            k = cv.waitKey(500)
 
            objpoints.append(objp)
            imgpoints_left.append(corners1)
            imgpoints_right.append(corners2)
 
    stereocalibration_flags = cv.CALIB_FIX_INTRINSIC
    ret, CM1, dist1, CM2, dist2, R, T, E, F = cv.stereoCalibrate(objpoints, imgpoints_left, imgpoints_right, mtx1, dist1, 
    mtx2, dist2, (width, height), criteria = criteria, flags = stereocalibration_flags)
 
    return R, T,ngoodpairs
dirpath='C:\\Users\\lahir\\fstack_data\\calibration\\'
mtx1, dist1,ngoodimages1 = calibrate_camera(images_folder = dirpath+'phone\\*')
mtx2, dist2,ngoodimages2 = calibrate_camera(images_folder = dirpath+'kinect\\*')
R, T,ngoodpaits = stereo_calibrate(mtx1, dist1, mtx2, dist2, dirpath+'phone\\*',dirpath+'kinect\\*')

#write the matrices to disk
savetxt(dirpath+'phone_calib.csv', mtx1, delimiter=',')
savetxt(dirpath+'phone_dist.csv', dist1, delimiter=',')
savetxt(dirpath+'kinect_calib.csv', mtx2, delimiter=',')
savetxt(dirpath+'kinect_dist.csv', dist2, delimiter=',')
savetxt(dirpath+'phonetoazure_R.csv', R, delimiter=',')
savetxt(dirpath+'phonetoazure_T.csv', T, delimiter=',')


