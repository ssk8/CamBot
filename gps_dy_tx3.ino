
#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include <TinyGPS++.h>


RF24 radio(7,8);
TinyGPSPlus gps;

const uint64_t pipes[2] = { 0xF0F0F0F0E1LL, 0xF0F0F0F0D2LL };

struct GPS_data {
  float latitude;
  float longitude;
  uint32_t gps_time;
  uint32_t gps_date;
  short speed;
  short course;
  int32_t altitude;
  bool rec = false;
} gps_data;

void setup(void)
{


  Serial.begin(115200);
  Serial1.begin(9600);
  radio.begin();
  radio.setPALevel(RF24_PA_LOW); // for testing
  //radio.setPALevel(RF24_PA_MAX);
 
  radio.enableDynamicPayloads();
  radio.setRetries(5,15);

  radio.openWritingPipe(pipes[0]);
  radio.openReadingPipe(1,pipes[1]);

  //radio.printDetails();
}

void loop(void)
{
   while (Serial1.available() > 0) gps.encode(Serial1.read());
  if (gps.location.isUpdated())
  {
    gps_data.latitude = gps.location.lat();
    gps_data.longitude = gps.location.lng();
    gps_data.gps_time = gps.time.value();
    gps_data.gps_date = gps.date.value();
    gps_data.speed = (short)gps.speed.mph();
    gps_data.course = (short)gps.course.value();
    gps_data.altitude = gps.altitude.value();
    gps_data.rec = false;
    
    Serial.print(gps.time.value());
    Serial.print("  ");
    Serial.println(gps_data.gps_time);
    Serial.println(sizeof(GPS_data));
    radio.write( &gps_data, sizeof(GPS_data) ); 
  }
  
}
