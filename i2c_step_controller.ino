#include <AccelStepper.h>
#include <Adafruit_DotStar.h>
#include <Wire.h>

#define nperRev 240000 
#define SLAVE_ADDRESS 0x08
#define STEPENABLEPIN 1
#define DIRPIN 3
#define STEPPIN 4
#define DATAPIN    7
#define CLOCKPIN   8 
#define DISABLE 2147483647
#define ENABLE 2147483646

AccelStepper stepper(AccelStepper::DRIVER, STEPPIN, DIRPIN);
Adafruit_DotStar strip(1, DATAPIN, CLOCKPIN, DOTSTAR_BRG);

uint32_t red = strip.Color(0, 55, 0);
uint32_t green = strip.Color(55, 0, 0);
uint32_t blue = strip.Color(0, 0, 55);


byte raw_data[3];
long rec_data = DISABLE;
long last_data;
long next_pos;
bool enabled;

void setup()
{ 
  //Serial.begin(115200);
  Wire.begin(SLAVE_ADDRESS);
  Wire.onReceive(receiveData); 
  stepper.setEnablePin(STEPENABLEPIN);
  stepper.setPinsInverted(false, false, true);
  stepper.disableOutputs ();
  enabled = false;
  stepper.setMaxSpeed(nperRev);
  stepper.setAcceleration(nperRev/20);
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
        next_pos = rec_data;
        if (enabled) {

          if (abs(stepper.currentPosition()-next_pos)>abs(stepper.currentPosition()-next_pos+nperRev)) next_pos-=nperRev;
          else if (abs(stepper.currentPosition()-next_pos)>abs(stepper.currentPosition()-next_pos-nperRev)) next_pos+=nperRev;
         
          long dist = abs(stepper.currentPosition()-next_pos);
          if (dist > 2000) stepper.setAcceleration(10000);
          else if (dist < 200) stepper.setAcceleration(200);
          else stepper.setAcceleration(dist*5-800);
          
          stepper.moveTo(next_pos);
      }
        else {
          stepper.setCurrentPosition(next_pos);
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

//  Serial.print("Current: ");
//  Serial.print(stepper.currentPosition());
//  Serial.print("  Target: ");
//  Serial.println(stepper.targetPosition());
  strip.show(); 
  stepper.run();
}


void receiveData(int bytecount)
{
  for (int i = 0; i < bytecount; i++) {
    raw_data[i] = Wire.read();
  }
  rec_data = 0;
  rec_data += raw_data[2] << 24;
  rec_data += raw_data[3] << 16;
  rec_data += raw_data[4] << 8;
  rec_data += raw_data[5];
}
