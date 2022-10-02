#include <iostream>
#include <iomanip>
#include <fstream>
#include <k4a/k4a.h>
#include <k4arecord/record.h>
#include <k4arecord/playback.h>


int main()
{
    uint64_t recording_length;
    k4a_imu_sample_t imu_sample;
    k4a_capture_t capture = NULL;
    k4a_stream_result_t result = K4A_STREAM_RESULT_SUCCEEDED;
    k4a_float3_t acc_val;
    k4a_float3_t gyro_val;
    uint64_t acc_ts;
    uint64_t gyro_ts;

    //create teh data file to write
    std::ofstream accfile;
    std::ofstream gyrofile;
    accfile.open("C:\\Users\\lahir\\source\\repos\\azurekinect\\azurekinect\\acc.csv");
    gyrofile.open("C:\\Users\\lahir\\source\\repos\\azurekinect\\azurekinect\\gyro.csv");

    std::cout << "Hello World!\n";
    k4a_playback_t playback_handle = NULL;
    if (k4a_playback_open("C:\\Users\\lahir\\source\\repos\\azurekinect\\azurekinect\\vid.mkv", &playback_handle) != K4A_RESULT_SUCCEEDED)
    {
        printf("Failed to open recording\n");
        goto Exit;
    }

    recording_length = k4a_playback_get_recording_length_usec(playback_handle);
    printf("Recording is %lld seconds long\n", recording_length / 1000000);


    while (result == K4A_STREAM_RESULT_SUCCEEDED)
    {
        result = k4a_playback_get_next_imu_sample(playback_handle, &imu_sample);
        if (result == K4A_STREAM_RESULT_SUCCEEDED)
        {
            // Process capture here
            acc_val = imu_sample.acc_sample;
            gyro_val = imu_sample.gyro_sample;
            acc_ts = imu_sample.acc_timestamp_usec;
            gyro_ts = imu_sample.gyro_timestamp_usec;
            if (accfile && gyrofile)
            {
                accfile << acc_ts<<",";
                accfile << std::fixed << std::setprecision(8) << acc_val.xyz.x;
                accfile << ",";
                accfile << std::fixed << std::setprecision(8) << acc_val.xyz.y;
                accfile << ",";
                accfile << std::fixed << std::setprecision(8) << acc_val.xyz.z;
                accfile << "\n";

                gyrofile << gyro_ts << ",";
                gyrofile << std::fixed << std::setprecision(8) << gyro_val.xyz.x;
                gyrofile << ",";
                gyrofile << std::fixed << std::setprecision(8) << gyro_val.xyz.y;
                gyrofile << ",";
                gyrofile << std::fixed << std::setprecision(8) << gyro_val.xyz.z;
                gyrofile << "\n";

            }

            //k4a_capture_release(capture);
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
        goto Exit;
    }

Exit:
    if (playback_handle != NULL)
    {
        k4a_playback_close(playback_handle);
    }
    if (accfile)
    {
        accfile.close();
    }
    if (gyrofile)
    {
        gyrofile.close();
    }
}
