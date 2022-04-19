# How to measure distance to objects with mono cameras 
A guide : https://medium.com/all-things-about-robotics-and-computer-vision/how-do-we-calculate-distances-of-objects-using-monocular-cameras-67c4822c538e

Discuss about how to used projection matrix and transformation matrix 
to transform from image to pixel coordinates.
If we have multiple cameras, we can use triangulation. But cannot do this for a single camera. 

A guide : https://pyimagesearch.com/2015/01/19/find-distance-camera-objectmarker-using-python-opencv/
We can use traiangle similarity to measure the distance to an object with known width
step 1 : measure the perceived focal length of camera (F)
		by placing an object with known width (W) at a known distance (D) in front of the camera 
		Then calculate the width in pixles.
		F=P*D/W

step 2: we can use traiangle similarity to measure distance 

The above methods uses a simple "pixles per metric" technique. But with proper camera calibration we can 
attain better results. We can use a checker board to do the calibration. 
Types of parameters :
    Extrinsic parameters are rotation and translation matrices used to convert something from the world frame to the camera frame
    Intrinsic parameters are the internal camera parameters, such as the focal length, to convert that information into a pixel
    
# Camera calibration using openCV
https://learnopencv.com/camera-calibration-using-opencv/





