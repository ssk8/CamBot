#include <AccelStepper.h>
#include <Adafruit_DotStar.h>
#include <Wire.h>


#define SLAVE_ADDRESS 0x08
#define STEPENABLEPIN 1
#define DIRPIN 3
#define STEPPIN 4
#define DATAPIN    7
#define CLOCKPIN   8
#define DISABLE 65279
#define ENABLE 65278

AccelStepper stepper(AccelStepper::DRIVER, STEPPIN, DIRPIN);
Adafruit_DotStar strip(1, DATAPIN, CLOCKPIN, DOTSTAR_BRG);

uint32_t red = strip.Color(0, 55, 0);
uint32_t green = strip.Color(55, 0, 0);
uint32_t blue = strip.Color(0, 0, 55);


byte raw_data[3];
uint16_t rec_data = DISABLE;
uint16_t last_data;
bool enabled;

void setup()
{ 
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData); 
  //Serial.begin(115200);
  stepper.setEnablePin(STEPENABLEPIN);
  stepper.setPinsInverted(false, false, true);
  stepper.disableOutputs ();
  enabled = false;
  stepper.setMaxSpeed(100.0);
  stepper.setAcceleration(100.0);
  stepper.setCurrentPosition(0);

  strip.begin();
  strip.setBrightness(80);
  strip.setPixelColor(0, green);
  strip.show(); 
  
}

void loop()
{
  if (last_data != rec_data) {
    if (rec_data == DISABLE) {
      stepper.disableOutputs();
      strip.setPixelColor(0, green);
      enabled = false;
    }
    else if (rec_data == ENABLE) {
      stepper.enableOutputs();
      strip.setPixelColor(0, red);
      enabled = true;
    }
    else
    { 
        if (enabled) {
          stepper.moveTo(rec_data);
      }
        else {
          stepper.setCurrentPosition(rec_data);
      }
    }
    last_data = rec_data;
  }

  
  if (enabled){
    if (stepper.isRunning()){
      strip.setPixelColor(0, blue);
    }
    else{
      strip.setPixelColor(0, red);
   }
  }
   
  strip.show(); 
  stepper.run();
}


void receiveData(int bytecount)
{
  for (int i = 0; i < bytecount; i++) {
    raw_data[i] = Wire.read();
  }
  rec_data=raw_data[2]*255+raw_data[3];
}
