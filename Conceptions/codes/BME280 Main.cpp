#include <Wire.h>
#include <Adafruit_BME280.h>

Adafruit_BME280 bme;

void setup() {
  Serial.begin(9600);
  while (!Serial); // Wait for serial port to connect (optional)
  
  // Check if sensor is found
  if (!bme.begin(0x76)) {
    Serial.println("Could not find BME280 sensor! Check wiring.");
    while (1); // Stop here if sensor not found
  }
  
  Serial.println("BME280 sensor found!");
}

void loop() {
  Serial.print("Temp = "); 
  Serial.print(bme.readTemperature()); 
  Serial.println(" °C");
  
  Serial.print("Pressure = "); 
  Serial.print(bme.readPressure() / 100.0F); 
  Serial.println(" hPa");
  
  Serial.print("Humidity = "); 
  Serial.print(bme.readHumidity()); 
  Serial.println(" %");
  
  Serial.println("---");
  delay(2000);
}