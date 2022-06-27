#include <ArduinoJson.h>
#include <Adafruit_MAX31865.h>
#include "SPI.h"

#include <Arduino_CRC32.h>

Arduino_CRC32 crc32;

// use hardware SPI, just pass in the CS pin
Adafruit_MAX31865 max_1 = Adafruit_MAX31865(10);
Adafruit_MAX31865 max_2 = Adafruit_MAX31865(9);
// The value of the Rref resistor. Use 430.0!
/*
//#define RREF1 432.1
//#define RREF2 429.2
*/
// Roof array pair
//*
#define RREF1 427.2
#define RREF2 430.9
//*/


void setup() {

  Serial.begin(115200,SERIAL_8E1);
  SPI.begin();
  max_1.begin(MAX31865_3WIRE);  // set to 2WIRE, 3WIRE or 4WIRE as necessary
  max_2.begin(MAX31865_3WIRE);
}

void loop() {
  if (Serial.available() > 0) {
    delay(10);
    while(Serial.available()) {
    Serial.read();
    } 
    //Serial.read();//read number of times.

    String s;
    s.reserve(255);
    String t1= String(max_1.temperature(100, RREF1));
    String r1= String(max_1.readRTD());
    String t2= String(max_2.temperature(100, RREF2));
    String r2= String(max_2.readRTD());
  
    // Check and print any faults
    uint8_t fault1 = max_1.readFault();
    uint8_t fault2 = max_2.readFault();

  String f1 = "";
  if (fault1) {
    f1 = String(fault1);
    max_1.clearFault();
  }

  String f2 = "";
  if (fault2) {
    f2 = String(fault2);
    max_2.clearFault();
  }

  const int capacity = JSON_ARRAY_SIZE(6) + 2*JSON_OBJECT_SIZE(2);
  StaticJsonDocument<capacity> doc;
  doc["t1"] = t1;
  doc["r1"] = r1;
  doc["t2"] = t2;
  doc["r2"] = r2;
  doc["f1"] = f1;
  doc["f2"] = f2;
  char output[128];
  serializeJson(doc,output);
  serializeJson(doc, Serial);
  Serial.println();
  Serial.read();
  }
}
