## Preparing data

### Save data (RGB,depth and IMU) from Azure Kinect to computer (to capture 30 frames at 30 frames per second)
```
 .\azurekinect.exe C:\\path\\to\\output\\file.mkv 30
 ```
 
 ### View metadata of the .mkv file with ffmpeg (you need ffmpeg installed in your system)
 ```
 ffmpeg -i .\file.mkv -f ffmetadata in.txt
 ```
 
 Note the field 
 ```
 K4A_START_OFFSET_NS: 200344000
 ```
 This is the starting timestamp of the video. All the timestamps are offsets of this.\
 Note stream numbers of different streams (e.g.  Stream #0:0)\
 Important streams :\
 COLOR - RGB images \
 TDEPTH - depth images from transformed to the point of view of the RGB camera
 
 ### Extract RGB and depth images from the video
 
 
