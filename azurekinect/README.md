## Preparing data

### Save data (RGB,depth and IMU) from Azure Kinect to computer (to capture 30 frames at 30 frames per second)
Goto stream directory
```
 .\stream.exe C:\\path\\to\\output\\file.mkv 30
 ```

### Save data (RGB,depth and IMU) from Azure Kinect to computer (to capture 40 frames at 30 frames per second)
```
 .\azurekinect.exe C:\\path\\to\\output\\file.mkv 40
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
 ```
 ffmpeg -skip_frame nokey -i .\vid.mkv -map 0:1 -vsync 0 -frame_pts true -r 10000 outputs/"originald%d.png"
 ```
 Here -map 0:1 is the stream number (0:1) \
 image files are named originald$timestamp_offset$.png\
 We need to add K4A_START_OFFSET_NS form earlier to this offset to get the actual timestamp of each image.\
 Execute this ffmpeg command twice; once to get RGB images, once to get depth images.
 
 ### Extract IMU data
 Goto reader directory 
 ```
  .\reader.exe C:\\output\\dir\\to\\acc_and_gyro\\csv_files\\  C:\\path\\to\\output\\file.mkv
 ```
 Format of the csv created : \
 timestamp of the IMU,x,y,z 
 
 
 
 
 
