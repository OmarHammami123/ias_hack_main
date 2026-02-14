#include <Audio.h>
#include <Wire.h>
#include <SPI.h>
#include <SD.h>

// Audio library objects
AudioInputI2S2          i2sMic;          // Use I2S2 for custom pins
AudioOutputUSB          usbOut;          // USB audio output
AudioConnection         patchCord1(i2sMic, 0, usbOut, 0); // Left channel
AudioConnection         patchCord2(i2sMic, 0, usbOut, 1); // Right channel (mono source)

void setup() {
  Serial.begin(9600);
  delay(1000);
  
  // Allocate sufficient audio memory
  AudioMemory(20);
  
  Serial.println("=================================");
  Serial.println("INMP441 → USB Audio Streaming");
  Serial.println("=================================");
  Serial.println("Pin Configuration:");
  Serial.println("  SD (Data)    -> Pin 7");
  Serial.println("  SCK (BCLK)   -> Pin 13");
  Serial.println("  WS (LRCLK)   -> Pin 11");
  Serial.println("  VCC          -> 3.3V");
  Serial.println("  GND          -> GND");
  Serial.println("  L/R          -> GND");
  Serial.println("=================================");
  Serial.println("Set USB Type to 'Audio' in Tools menu!");
  Serial.println();
}

void loop() {
  // Monitor CPU and memory usage
  static unsigned long lastPrint = 0;
  if (millis() - lastPrint > 2000) {
    lastPrint = millis();
    
    Serial.print("CPU Usage: ");
    Serial.print(AudioProcessorUsage());
    Serial.print("%  |  Memory: ");
    Serial.print(AudioMemoryUsage());
    Serial.print("/");
    Serial.println(AudioMemoryUsageMax());
  }
}