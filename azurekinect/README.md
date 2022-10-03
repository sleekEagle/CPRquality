## Preparing data

### Save data (RGB,depth and IMU) from Azure Kinect to computer (to capture 30 frames at 30 frames per second)
```
 .\azurekinect.exe C:\\path\\to\\output\\file.mkv 30
 ```
 
 ### View metadata of the .mkv file with ffmpeg (you need ffmpeg installed in your system)
 ```
 ffmpeg -i .\file.mkv -f ffmetadata in.txt
 ```
 
 
