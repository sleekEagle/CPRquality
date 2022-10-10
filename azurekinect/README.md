## Preparing data

### Save data (RGB,depth and IMU) from Azure Kinect to computer (to capture 30 frames at 30 frames per second)
Goto stream directory
```
 .\stream.exe out_path_of_video out_path_for_ts_file required_fps
 .\stream.exe C:\\Users\\lahir\\CPRdata\\vid.mkv C:\\Users\\lahir\\CPRdata\\ 300
 ```
 required_fps : [30,15,5]\
 required_fps=-1 : capture till CTRL+C\
 We can use Azure Kinect Viewer to view the video .mkvfile. Regular video players will not work. \
 Azure Kinect Viewer : https://learn.microsoft.com/en-us/azure/kinect-dk/azure-kinect-viewer \
 outputs : \
 1. vid.mkv with the rgb,depth and IMU tracks \
 2. ts.txt file with computer timestamps of each capture 

### E.g. Save data (RGB,depth and IMU) from Azure Kinect to computer (to capture 40 frames at 30 frames per second)
```
 .\stream.exe C:\\path\\to\\output\\file.mkv C:\\path\\to\\output\\ 40
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
 the directory output must be present. Otherwise there will be an error thrown.\
 We need to add K4A_START_OFFSET_NS form earlier to this offset to get the actual timestamp of each image.\
 Execute this ffmpeg command twice; once to get RGB images, once to get depth images.
 
 ### Extract IMU data
 Goto IMUreader directory 
 ```
.\IMUreader.exe C:\\Users\\lahir\\CPRdata\\ C:\\Users\\lahir\\CPRdata\\vid.mkv
 ```
 outputs : \
 acc.csv , gyro.csv files with IMU data created in the same directory as the video file \
 Format of the csv created : \
 timestamp of the IMU,x,y,z 

 ### Extract the depth images transformed to the RGB coordinate system
  
 
 
 
 
 
