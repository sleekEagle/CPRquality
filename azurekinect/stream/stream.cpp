#define _CRT_SECURE_NO_DEPRECATE
#include <stdio.h>
#include <stdlib.h>
#include <k4a/k4a.h>
#include <iostream>
#include <k4arecord/record.h>
#include <signal.h>
#include <conio.h>
#include <cstdlib>
#include <iostream>
#include <fstream>
#include <string> 
#include <inttypes.h>
#include <chrono>
#include <vector>
#include <sstream>

using namespace std;
using namespace std::chrono;

volatile sig_atomic_t stop;


static bool k4a_convert_resolution_to_width_height(k4a_color_resolution_t resolution,
    uint32_t* width_out,
    uint32_t* height_out)
{
    uint32_t width = 0;
    uint32_t height = 0;
    switch (resolution)
    {
    case K4A_COLOR_RESOLUTION_720P:
        width = 1280;
        height = 720;
        break;
    case K4A_COLOR_RESOLUTION_1080P:
        width = 1920;
        height = 1080;
        break;
    case K4A_COLOR_RESOLUTION_1440P:
        width = 2560;
        height = 1440;
        break;
    case K4A_COLOR_RESOLUTION_1536P:
        width = 2048;
        height = 1536;
        break;
    case K4A_COLOR_RESOLUTION_2160P:
        width = 3840;
        height = 2160;
        break;
    case K4A_COLOR_RESOLUTION_3072P:
        width = 4096;
        height = 3072;
        break;
    default:
        return false;
    }

    if (width_out != NULL)
        *width_out = width;
    if (height_out != NULL)
        *height_out = height;
    return true;
}

void inthand(int signum) {
    stop = 1;
}


int main(int argc, char** argv)
{
    static const int32_t defaultExposureAuto = -12;
    static const int32_t defaultGainAuto = -1;
    int returnCode = 1;
    k4a_device_t device = NULL;
    const int32_t TIMEOUT_IN_MS = 1000;
    //-1 : capturing until CTRL+C, otherwise number of frames captured
    int captureFrameCount= atoi(argv[3]);
    printf("captureframe count = % d\n",captureFrameCount);
    k4a_capture_t capture = NULL;
    FILE* fptr;
    ofstream tsfile;
    string tsfilename = "ts.txt";
    char* filename;
    int absoluteExposureValue = defaultExposureAuto;
    int gain = defaultGainAuto;
    bool firstphoto = false;

    uint32_t color_width, color_height;

    signal(SIGINT, inthand);

    uint32_t device_count = k4a_device_get_installed_count();

    if (argc < 2) {
        printf("Need at least 2 args. Exiting..\n");
        goto Exit;
    }

    if (device_count == 0)
    {
        printf("No K4A devices found\n");
        return 0;
    }

    if (K4A_RESULT_SUCCEEDED != k4a_device_open(K4A_DEVICE_DEFAULT, &device))
    {
        printf("Failed to open device\n");
        goto Exit;
    }
    printf("device opened!\n");

    

    k4a_device_configuration_t config = K4A_DEVICE_CONFIG_INIT_DISABLE_ALL;
    config.camera_fps = K4A_FRAMES_PER_SECOND_30;
    config.color_format = K4A_IMAGE_FORMAT_COLOR_BGRA32;
    config.color_resolution = K4A_COLOR_RESOLUTION_720P;
    config.depth_mode = K4A_DEPTH_MODE_NFOV_UNBINNED;
    config.synchronized_images_only = true;
    

    if (K4A_RESULT_SUCCEEDED != k4a_device_start_cameras(device, &config))
    {
        printf("Failed to start device\n");
        goto Exit;
    }
    printf("Opened camera!\n");
    if (K4A_RESULT_SUCCEEDED != k4a_device_start_imu(device))
    {
        printf("Failed to start IMUs\n");
        goto Exit;
    }
    printf("IMUs started\n");
   


    k4a_record_t recording;
    if (K4A_RESULT_SUCCEEDED != k4a_record_create(argv[1], device, config, &recording))
    {
        printf("Failed to create record \n");
        goto Exit;
    }
    if (K4A_RESULT_SUCCEEDED != k4a_record_add_imu_track(recording))
    {
        printf("Failed to add IMU track to record\n");
        goto Exit;
    }

    k4a_convert_resolution_to_width_height(config.color_resolution, &color_width, &color_height);

    if (K4A_RESULT_SUCCEEDED != k4a_record_write_header(recording))
    {
        printf("Failed to write header \n");
        goto Exit;
    }
 
    printf("Capturing first image....\n");
    while (!firstphoto)
    {
        switch (k4a_device_get_capture(device, &capture, TIMEOUT_IN_MS))
        {
        case K4A_WAIT_RESULT_SUCCEEDED:
            firstphoto = true;
            break;
        case K4A_WAIT_RESULT_TIMEOUT:
            printf("Timed out waiting for a capture\n");
            break;
        case K4A_WAIT_RESULT_FAILED:
            printf("Failed to read a capture\n");
            goto Exit;
        }
    }
    printf("Done Capturing first image....\n");
    k4a_capture_release(capture);
    printf("Streraming images...\n");

    char c;
    uint64_t depthts;

    //open file to write ts
    filename = (char*)malloc(strlen(argv[2]) + strlen(tsfilename.c_str()));
    strcpy(filename, argv[2]);
    filename += strlen(argv[2]);
    strcpy(filename, tsfilename.c_str());
    filename += strlen(tsfilename.c_str());
    filename -= (strlen(argv[2]) + strlen(tsfilename.c_str()));
    printf("Openning ts file:  %s\n", filename);
    tsfile.open(filename);

    while ((!stop) && (captureFrameCount == -1)||(captureFrameCount-- > 0))
    {


        switch (k4a_device_get_capture(device, &capture, TIMEOUT_IN_MS))
        {
        case K4A_WAIT_RESULT_SUCCEEDED:
            break;
        case K4A_WAIT_RESULT_TIMEOUT:
            printf("Timed out waiting for a capture\n");
            continue;
            break;
        case K4A_WAIT_RESULT_FAILED:
            printf("Failed to read a capture\n");
            goto Exit;
        }
        char capturets_s[21];
        uint64_t ts = duration_cast<milliseconds>(system_clock::now().time_since_epoch()).count();
        sprintf(capturets_s, "%" PRIu64, ts);

        //write ts to file
        
        tsfile << capturets_s<<"\n";


        if (K4A_RESULT_SUCCEEDED != k4a_record_write_capture(recording, capture))
        {
            printf("Failed to write to record \n");
            goto Exit;
        }

        //getting IMU sample
        k4a_imu_sample_t sample;
        if (K4A_RESULT_SUCCEEDED != k4a_device_get_imu_sample(device, &sample, 0))
        {
            printf("Failed to get IMU sample\n");
            goto Exit;
        }
        if (K4A_RESULT_SUCCEEDED != k4a_record_write_imu_sample(recording, sample))
        {
            printf("Failed to write IMU sample to record\n");
            goto Exit;
        }
       
        
      
        milliseconds ms = duration_cast<milliseconds>(
            system_clock::now().time_since_epoch()
            );

       
        // release capture
        k4a_capture_release(capture);
        fflush(stdout);
    }

    //stopping IMU and cameras
    k4a_device_stop_cameras(device);
    k4a_device_stop_imu(device);

    //closing up recording
    if (K4A_RESULT_SUCCEEDED != k4a_record_flush(recording))
    {
        printf("Failed to flush to record file... \n");
        goto Exit;
    }
    printf("Flushed to record file.....\n");
    k4a_record_close(recording);
    

    returnCode = 0;
Exit:
    if (device != NULL)
    {
        k4a_device_close(device);
    }
    if (tsfile) 
    {
        tsfile.close();
    }

    return returnCode;
    
}

