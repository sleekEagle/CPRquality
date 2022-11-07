# How to measure depth with Azure kinect and depth sensor
## Step 1 do CPR and capture video with Azure Kinect
1. Run the azurekinect/stream/stream.exe that captures IMU+depth+RGB stream from azure kinect camera
e.g:
C:\Users\lahir\code\CPRquality\azurekinect\stream\stream.exe C:\\Users\\lahir\\CPRdata\\vid.mkv C:\\Users\\lahir\\CPRdata\\ 600
argument 1 : output file (.mkv contains all the data (IMU+depth+RGB))
argument 2 : number of seconds that the capture captures data

2.  Run azurekinect/IMUreader/IMUreader.exe to extract the IMU data from the captured .mkv file
C:\Users\lahir\code\CPRquality\azurekinect\IMUreader\IMUreader.exe C:\\Users\\lahir\\CPRdata\\ C:\\Users\\lahir\\CPRdata\\vid.mkv
argument 1 : output data directory
argument 2 : input data file
output : acc.csv and gyro.csv that contains timestamped accelerometer and gyroscope data 
format : 
timestamp,x_value, y_value   , z_value
200333,5.52886009,-0.02718589,-8.26961422





