#define _CRT_SECURE_NO_DEPRECATE
#include <iostream>
#include <iomanip>
#include <fstream>
#include <k4a/k4a.h>
#include <k4arecord/record.h>
#include <k4arecord/playback.h>
#include <sstream>
#include <string> 

using namespace std;


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


int writefile(const k4a_image_t image, char* filename)
{
    ofstream myfile;
    uint8_t* buffer = k4a_image_get_buffer(image);
    size_t imgsize = k4a_image_get_size(image);
    int hpixels = k4a_image_get_height_pixels(image);
    int wpixels = k4a_image_get_width_pixels(image);

    printf(" |writing image res:%4dx%4d stride:%5d\n",
        hpixels,
        wpixels,
        k4a_image_get_width_pixels(image),
        k4a_image_get_stride_bytes(image));
    printf("imgsize = %zu\n", imgsize);
    int numbits = 0;
    printf("writing to file %s\n", filename);
    myfile.open(filename);
    if (!myfile) {
        printf("Exception opening file\n");
        return -1;
    }
    try {
        for (int i = 0;i < imgsize - 1;i += 2) {
            //uint16_t val = ((uint16_t)buffer[i] << 8) | buffer[i + 1];
            uint16_t val = buffer[i] + (buffer[i + 1] << 8);
            char str[80];
            int str_len = sprintf(str, "%d", val);
            //printf("int : %u string %s\n",val,str);
            myfile << str;
            if (i != (imgsize - 2)) myfile << ",";
            numbits += 1;
        }
    }
    catch (ios_base::failure) {
        printf("Exception writing to file\n");
        return -1;
    }
    printf("Wrote %d bytes\n", numbits);
    myfile.close();
    return 0;
}

void print_img_stats(const k4a_image_t image)
{
    printf(" | image res:%4dx%4d stride:%5d\n",
        k4a_image_get_height_pixels(image),
        k4a_image_get_width_pixels(image),
        k4a_image_get_stride_bytes(image));

    uint8_t* buffer = k4a_image_get_buffer(image);
    size_t imgsize = k4a_image_get_size(image);
    printf("num pixles = %d\n",
        k4a_image_get_height_pixels(image) * k4a_image_get_width_pixels(image));
    printf("im size = %zu \n", imgsize);

    uint16_t sum = 0;
    uint16_t max = 0;
    for (int i = 0;i < imgsize - 1;i += 2) {
        uint16_t val = ((uint16_t)buffer[i] << 8) | buffer[i + 1];
        sum += val;
        if (val > max) max = val;
    }
    double avg = (double)sum / (double)(k4a_image_get_height_pixels(image) * k4a_image_get_width_pixels(image));
    printf("mean pixel value = %f\n", avg);
    printf("max pixel value = %d\n", max);
}


int main(int argc, char** argv)
{
    uint64_t recording_length;
    k4a_imu_sample_t imu_sample;
    k4a_capture_t capture = NULL;
    k4a_stream_result_t result = K4A_STREAM_RESULT_SUCCEEDED;
    k4a_calibration_t calibration;
    k4a_transformation_t transformation = NULL;
    k4a_device_t device = NULL;
    k4a_playback_t playback_handle = NULL;
    uint32_t color_width, color_height;

    k4a_image_t transformed_depth_image = NULL;
    k4a_image_t point_cloud_image = NULL;
    k4a_image_t colorimage;
    k4a_image_t depthimage;

    std::string n_capture_s;
    int n_capture = 0;


    //define transformations

    k4a_device_configuration_t config = K4A_DEVICE_CONFIG_INIT_DISABLE_ALL;
    config.camera_fps = K4A_FRAMES_PER_SECOND_30;
    config.color_format = K4A_IMAGE_FORMAT_COLOR_BGRA32;
    config.color_resolution = K4A_COLOR_RESOLUTION_720P;
    config.depth_mode = K4A_DEPTH_MODE_NFOV_UNBINNED;
    config.synchronized_images_only = true;


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
    if (K4A_RESULT_SUCCEEDED !=
        k4a_device_get_calibration(device, config.depth_mode, config.color_resolution, &calibration))
    {
        printf("Failed to get calibration\n");
        goto Exit;
    }
    transformation = k4a_transformation_create(&calibration);


    //create empty images to hold transfpormed depth and point cloud images
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
    //create point cloud image 
    if (K4A_RESULT_SUCCEEDED != k4a_image_create(K4A_IMAGE_FORMAT_CUSTOM,
        color_width,
        color_height,
        color_width * 3 * (int)sizeof(int16_t),
        &point_cloud_image))
    {
        printf("Failed to create point cloud image\n");
        return false;
    }
    if (transformed_depth_image)
    {
        printf(" | Transformed color res:%4dx%4d stride:%5d ",
            k4a_image_get_height_pixels(transformed_depth_image),
            k4a_image_get_width_pixels(transformed_depth_image),
            k4a_image_get_stride_bytes(transformed_depth_image));

    }
    else
    {
        printf(" | Transformed color None                       ");
    }

    printf("Opening video file at %s\n", argv[1]);

    if (k4a_playback_open(argv[1], &playback_handle) != K4A_RESULT_SUCCEEDED)
    {
        printf("Failed to open recording\n");
        goto Exit;
    }

    recording_length = k4a_playback_get_recording_length_usec(playback_handle);
    printf("Recording is %lld seconds long\n", recording_length / 1000000);

    n_capture = 0;

    while (result == K4A_STREAM_RESULT_SUCCEEDED)
    {
        result = k4a_playback_get_next_capture(playback_handle, &capture);
        if (result == K4A_STREAM_RESULT_SUCCEEDED)
        {
            
            // Process capture here

            // Probe for color image
            colorimage = k4a_capture_get_color_image(capture);
            // Probe for a depth16 image
            depthimage = k4a_capture_get_depth_image(capture);
            
            //transform depth image into color coordinates
            if (K4A_RESULT_SUCCEEDED != k4a_transformation_depth_image_to_color_camera(transformation, depthimage, transformed_depth_image))
            {
                printf("Failed to transform depth image to color camera\n");
                goto Exit;
            }
            if (K4A_RESULT_SUCCEEDED != k4a_transformation_depth_image_to_point_cloud(transformation,
                transformed_depth_image,
                K4A_CALIBRATION_TYPE_COLOR,
                point_cloud_image))
            {
                printf("Failed to compute point cloud\n");
                goto Exit;
            }
            printf("i=%d\n", n_capture);

            
            n_capture_s = std::to_string(n_capture);
            
            char* filename = (char*)malloc(strlen(argv[2]) + strlen(n_capture_s.c_str()) + 4);
            
            strcpy(filename, argv[2]);
            filename += strlen(argv[2]);
            strcpy(filename, n_capture_s.c_str());
            filename += strlen(n_capture_s.c_str());
            strcpy(filename, ".trn");
            filename -= (strlen(argv[2]) + strlen(n_capture_s.c_str()));
            printf("before writing to file %s\n", filename);
            writefile(transformed_depth_image, filename);
            printf("i=%d\n", n_capture);
            
            //write pt cloud to file
            
            filename = (char*)malloc(strlen(argv[2]) + strlen(n_capture_s.c_str()) + 4);
            strcpy(filename, argv[2]);
            filename += strlen(argv[2]);
            strcpy(filename, n_capture_s.c_str());
            filename += strlen(n_capture_s.c_str());
            strcpy(filename, ".ptc");
            filename -= (strlen(argv[2]) + strlen(n_capture_s.c_str()));
            printf("before writing to file pt cloud %s\n", filename);
            writefile(point_cloud_image, filename);
            

            k4a_capture_release(capture);
            
            n_capture++;
        }
        else if (result == K4A_STREAM_RESULT_EOF)
        {
            // End of file reached
            break;
        }
    }
    if (result == K4A_STREAM_RESULT_FAILED)
    {
        printf("Failed to read entire recording\n");
        return 1;
    }

    k4a_image_release(transformed_depth_image);



Exit:
    if (playback_handle != NULL)
    {
        k4a_playback_close(playback_handle);
    }
    if (device != NULL)
    {
        k4a_device_close(device);
    }
  
}
