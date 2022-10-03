#define _CRT_SECURE_NO_DEPRECATE
#include <stdio.h>
#include <stdlib.h>
#include <k4a/k4a.h>
#include <iostream>
#include <opencv2/opencv.hpp>
#include <opencv2/imgcodecs.hpp>
#include <k4arecord/record.h>
#include <signal.h>
#include <conio.h>
#include <cstdlib>

using namespace cv;
using namespace std;

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
    if (argc < 2)
    {
        printf("Need at least 2 arguments. Exiting...\n");
        goto Exit;
    }
    printf("Starting the stream program...\n");
    static const int32_t defaultExposureAuto = -12;
    static const int32_t defaultGainAuto = -1;
    int returnCode = 1;
    k4a_device_t device = NULL;
    const int32_t TIMEOUT_IN_MS = 1000;
    //-1 : capturing until CTRL+C, otherwise number of frames captured
    int captureFrameCount= atoi(argv[2]);
    printf("captureframe count = % d\n",captureFrameCount);
    k4a_capture_t capture = NULL;
    k4a_transformation_t transformation = NULL;
    FILE* fptr;
    int absoluteExposureValue = defaultExposureAuto;
    int gain = defaultGainAuto;
    bool firstphoto = false;

    uint32_t color_width, color_height;
    k4a_image_t transformed_depth_image = NULL;

    signal(SIGINT, inthand);

    struct BITMAPINFOHEADER
    {
        uint32_t biSize = sizeof(BITMAPINFOHEADER);
        uint32_t biWidth;
        uint32_t biHeight;
        uint16_t biPlanes = 1;
        uint16_t biBitCount;
        uint32_t biCompression;
        uint32_t biSizeImage;
        uint32_t biXPelsPerMeter = 0;
        uint32_t biYPelsPerMeter = 0;
        uint32_t biClrUsed = 0;
        uint32_t biClrImportant = 0;
    };

   
    uint32_t device_count = k4a_device_get_installed_count();

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
    

    k4a_calibration_t calibration;
    if (K4A_RESULT_SUCCEEDED !=
        k4a_device_get_calibration(device, config.depth_mode, config.color_resolution, &calibration))
    {
        printf("Failed to get calibration\n");
        goto Exit;
    }
    transformation = k4a_transformation_create(&calibration);

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
    if (K4A_RESULT_SUCCEEDED != k4a_image_create(K4A_IMAGE_FORMAT_DEPTH16,
        color_width,
        color_height,
        color_width * 2,
        &transformed_depth_image))
    {
        printf("Failed to create transformed color image\n");
        return false;
    }
    if (transformed_depth_image)
    {
        printf(" | Transformed color res:%4dx%4d stride:%5d ",
            k4a_image_get_height_pixels(transformed_depth_image),
            k4a_image_get_width_pixels(transformed_depth_image),
            k4a_image_get_stride_bytes(transformed_depth_image));

        BITMAPINFOHEADER depth_codec_header;
        depth_codec_header.biWidth = color_width;
        depth_codec_header.biHeight = color_height;
        depth_codec_header.biBitCount = 16;
        depth_codec_header.biCompression = 0x67363162; // b16g
        depth_codec_header.biSizeImage = sizeof(uint16_t) * color_width * color_height;
        k4a_record_video_settings_t depth_video_settings;
        depth_video_settings.width = color_width;
        depth_video_settings.height = color_height;
        depth_video_settings.frame_rate = config.camera_fps;
        if (K4A_RESULT_SUCCEEDED != k4a_record_add_custom_video_track(recording,
            "TDEPTH",
            "V_MS/VFW/FOURCC",
            reinterpret_cast<const uint8_t*>(&depth_codec_header),
            sizeof(depth_codec_header),
            &depth_video_settings))
        {
            printf("Failed to add custom depth track to video...\n");
            goto Exit;
        }

    }
    else
    {
        printf(" | Transformed color None                       ");
    }

    
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

    char c;
    while ((!stop) && (captureFrameCount == -1)||(captureFrameCount-- > 0))
    {
        k4a_image_t colorimage;
        k4a_image_t depthimage;


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

        if (K4A_RESULT_SUCCEEDED != k4a_record_write_capture(recording, capture))
        {
            printf("Failed to write to record \n");
            goto Exit;
        }

        //k4a_record_write_capture(recording, capture);
        //k4a_capture_release(capture);

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
        

        /*
        // Probe for a color image
        colorimage = k4a_capture_get_color_image(capture);
        if (colorimage)
        {
            printf(" | Color res:%4dx%4d stride:%5d ",
                k4a_image_get_height_pixels(colorimage),
                k4a_image_get_width_pixels(colorimage),
                k4a_image_get_stride_bytes(colorimage));
            k4a_image_release(colorimage);
        }
        else
        {
            printf(" | Color None                       ");
        }
        */  
        
        // Probe for a depth16 image
        depthimage = k4a_capture_get_depth_image(capture);
        if (depthimage != NULL)
        {
            //printf(" | Depth16 res:%4dx%4d stride:%5d\n",
            //    k4a_image_get_height_pixels(depthimage),
            //   k4a_image_get_width_pixels(depthimage),
            //  k4a_image_get_stride_bytes(depthimage));

            //transform depth image into color coordinates
            if (K4A_RESULT_SUCCEEDED != k4a_transformation_depth_image_to_color_camera(transformation, depthimage, transformed_depth_image))
            {
                printf("Failed to transform depth image to color camera\n");
                goto Exit;
            }
            if (K4A_RESULT_SUCCEEDED != k4a_record_write_custom_track_data(recording,
                "TDEPTH",
                k4a_image_get_device_timestamp_usec(depthimage),
                k4a_image_get_buffer(transformed_depth_image),
                k4a_image_get_size(transformed_depth_image)))
            {
                printf("Failed to write custom depth track to record...\n");
                goto Exit;
            }
            ;
            k4a_image_release(depthimage);
        }
        else
        {
            printf(" | Depth16 None\n");
        }

        // release capture
        k4a_capture_release(capture);
        fflush(stdout);
    }

    //stopping IMU and cameras
    k4a_image_release(transformed_depth_image);
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

    return returnCode;
    
}

