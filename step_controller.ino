#include <AccelStepper.h>
#include <Adafruit_DotStar.h>

#define STEPENABLEPIN 0
#define DIRPIN 3
#define STEPPIN 4
#define DATAPIN    7
#define CLOCKPIN   8

AccelStepper stepper(AccelStepper::DRIVER, STEPPIN, DIRPIN);
Adafruit_DotStar strip(1, DATAPIN, CLOCKPIN, DOTSTAR_BRG);

uint32_t red = strip.Color(0, 55, 0);
uint32_t green = strip.Color(55, 0, 0);
uint32_t blue = strip.Color(0, 0, 55);

String inputString = "";
bool enabled = false;

void setup()
{  
  Serial.begin(115200);
  stepper.setEnablePin(STEPENABLEPIN);
  stepper.setPinsInverted(false, false, true);
  stepper.disableOutputs ();
  stepper.setMaxSpeed(100.0);
  stepper.setAcceleration(1000.0);
  stepper.setCurrentPosition(0);

  strip.begin();
  strip.setBrightness(80);
  strip.setPixelColor(0, green);
  strip.show(); 
  
}

void loop()
{
  if (Serial.available() > 0) {
    inputString = Serial.readString();
    if (inputString == "en") {
      stepper.enableOutputs();
      enabled = true;
    }
    else if (inputString == "dis") {
      stepper.disableOutputs();
      enabled = false;
    }
    else {
    stepper.moveTo(inputString.toInt());
    }
  }
  if (enabled){
      if (stepper.isRunning()){
        strip.setPixelColor(0, blue);
      }
      else{
        strip.setPixelColor(0, red);
      }
  }
  else{
    strip.setPixelColor(0, green);
    stepper.setCurrentPosition(0);
    }
  strip.show(); 
  stepper.run();
}
