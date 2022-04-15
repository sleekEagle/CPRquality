#include <Wire.h>
#include "Adafruit_VL6180X.h"

Adafruit_VL6180X vl = Adafruit_VL6180X();

void setup() {
  Serial.begin(115200);

  // wait for serial port to open on native usb devices
  while (!Serial) {
    delay(1);
  }
  
  Serial.println("Adafruit VL6180x test!");
  if (! vl.begin()) {
    Serial.println("Failed to find sensor");
    while (1);
  }
  Serial.println("Sensor found!");
}

void loop() {
  //float lux = vl.readLux(VL6180X_ALS_GAIN_5);

  //Serial.print("Lux: "); Serial.println(lux);
  float range=0;
  uint8_t count=0;
  //sample period to take mean in ms
  uint8_t period=25;

  unsigned long StartTime = millis();
  
  for(int i=0;i<=period;i++){
    count++;
    
    uint8_t status = vl.readRangeStatus();

    // Some error occurred, print it out!
  
    if  ((status >= VL6180X_ERROR_SYSERR_1) && (status <= VL6180X_ERROR_SYSERR_5)) {
      Serial.println("System error");
      break;
    }
    else if (status == VL6180X_ERROR_ECEFAIL) {
      Serial.println("ECE failure");
      break;
    }
    else if (status == VL6180X_ERROR_NOCONVERGE) {
      Serial.println("No convergence");
    }
    else if (status == VL6180X_ERROR_RANGEIGNORE) {
      Serial.println("Ignoring range");
      break;
    }
    else if (status == VL6180X_ERROR_SNR) {
      Serial.println("Signal/Noise error");
      break;
    }
    else if (status == VL6180X_ERROR_RAWUFLOW) {
      Serial.println("Raw reading underflow");
      break;
    }
    else if (status == VL6180X_ERROR_RAWOFLOW) {
      Serial.println("Raw reading overflow");
      break;
    }
    else if (status == VL6180X_ERROR_RANGEUFLOW) {
      Serial.println("Range reading underflow");
      break;
    }
    else if (status == VL6180X_ERROR_RANGEOFLOW) {
      Serial.println("Range reading overflow");
      break;
    } 

    if (status == VL6180X_ERROR_NONE) {
      range+=vl.readRange();
    }
    //delay(1);
   }

  unsigned long CurrentTime = millis();
  unsigned long ElapsedTime = CurrentTime - StartTime;
  
  Serial.print("count: "); Serial.println(count-1);
   if(count==period+1){
     float dist=range/period;
     Serial.print("Range: "); Serial.println(dist);
     Serial.print("Elapsed Time: "); Serial.println(ElapsedTime);
   }
 
}
