#include <SPI.h>
#include "nRF24L01.h"
#include "RF24.h"
#include <TinyGPS++.h>
#include <EasyButton.h>


#define LED_PIN 13
#define BUTTON_1_PIN 10
bool button1_state = false;


RF24 radio(A4,A5);
TinyGPSPlus gps;

EasyButton button1(BUTTON_1_PIN);

const uint64_t pipes[2] = { 0xF0F0F0F0E1LL, 0xF0F0F0F0D2LL };

struct GPS_data {
  float latitude;
  float longitude;
  uint32_t gps_time;
  uint32_t gps_date;
  short speed;
  short course;
  int32_t altitude;
  bool button1 = false;
  bool button2 = false;
  bool button3 = false;  
  bool button4 = false;
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

  pinMode(LED_PIN, OUTPUT);

  pinMode(BUTTON_1_PIN,INPUT_PULLUP);
  button1.onPressed(buttonPressed);
  button1.onSequence(2, 500, sequenceEllapsed);
  button1.enableInterrupt(buttonISR);
  button1.read();
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
    gps_data.button1 = button1_state;
    
//    Serial.print(gps.time.value());
//    Serial.print("  ");
//    Serial.println(gps_data.gps_time);
//    Serial.println(sizeof(GPS_data));
    radio.write( &gps_data, sizeof(GPS_data) ); 
  }
  
}


void buttonPressed()
{
  button1_state = !button1_state;
  //Serial.print("rec=");
  if (button1_state){
    digitalWrite(LED_PIN, HIGH);
  }
  else{
    digitalWrite(LED_PIN, LOW);
    }
}

void sequenceEllapsed()
{
  Serial.println("Double click");
}

void buttonISR()
{
  button1.read();
}
