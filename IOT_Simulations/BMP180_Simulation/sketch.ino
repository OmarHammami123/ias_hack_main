#include <Wire.h>
#include <Adafruit_BMP085.h>

Adafruit_BMP085 bmp;

// Generic ESP32 default I2C pins
constexpr uint8_t SDA_PIN = 21;
constexpr uint8_t SCL_PIN = 22;
constexpr uint32_t I2C_FREQ = 100000;   // 100kHz
constexpr float SEA_LEVEL_PA = 101325.0; // standard sea-level pressure

void setup() {
  Serial.begin(115200);
  delay(500);

  // Start I2C on chosen pins
  Wire.begin(SDA_PIN, SCL_PIN, I2C_FREQ);

  if (!bmp.begin()) {
    Serial.println("BMP180 not detected. Check wiring/power.");
    while (true) {
      delay(1000);
    }
  }

  Serial.println("BMP180 detected. Reading data...");
}

void loop() {
  float tempC = bmp.readTemperature();
  int32_t pressurePa = bmp.readPressure();
  float altitudeM = bmp.readAltitude(SEA_LEVEL_PA);
  float seaLevelPa = bmp.readSealevelPressure();

  Serial.print("Temperature: ");
  Serial.print(tempC, 2);
  Serial.println(" C");

  Serial.print("Pressure: ");
  Serial.print(pressurePa);
  Serial.println(" Pa");

  Serial.print("Altitude (est.): ");
  Serial.print(altitudeM, 2);
  Serial.println(" m");

  Serial.print("Sea-level pressure (calc): ");
  Serial.print(seaLevelPa, 1);
  Serial.println(" Pa");

  Serial.println("---------------------------");
  delay(2000);
}
