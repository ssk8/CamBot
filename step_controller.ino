#include <AccelStepper.h>
#include <Adafruit_DotStar.h>

#define DATAPIN    7
#define CLOCKPIN   8

static const int stepPin = 4, dirPin = 3, stepperEnablePin = 0;
AccelStepper stepper(AccelStepper::DRIVER, stepPin, dirPin);
Adafruit_DotStar strip(1, DATAPIN, CLOCKPIN, DOTSTAR_BRG);
uint32_t red = strip.Color(0, 55, 0);
uint32_t green = strip.Color(55, 0, 0);

String inputString = "";

void setup()
{  
  Serial.begin(115200);
  stepper.setEnablePin(stepperEnablePin);
  stepper.setPinsInverted(false, false, true);
  stepper.disableOutputs ();
  stepper.setMaxSpeed(400.0);
  stepper.setAcceleration(100.0);
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
      strip.setPixelColor(0, red);
      strip.show(); 
    }
    else if (inputString == "dis") {
      stepper.disableOutputs();
      strip.setPixelColor(0, green);
      strip.show(); 
    }
    else {
    stepper.moveTo(inputString.toInt());
    }
    Serial.println(inputString);
  }
  stepper.run();
}

