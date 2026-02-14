#include <Audio.h>

AudioInputI2S2          i2sMic;
AudioOutputUSB          usbOut;
AudioAnalyzePeak        peak;
AudioConnection         patch1(i2sMic, 0, usbOut, 0);
AudioConnection         patch2(i2sMic, 0, usbOut, 1);
AudioConnection         patch3(i2sMic, 0, peak, 0);

void setup() {
  Serial.begin(9600);
  delay(2000);
  
  Serial.println("=================================");
  Serial.println("INMP441 DEBUG MODE");
  Serial.println("=================================");
  
  // Initialize audio
  AudioMemory(20);
  
  Serial.println("✓ Audio library initialized");
  Serial.println();
  Serial.println("Pin Configuration:");
  Serial.println("  INMP441 SD   -> Teensy Pin 7  (I2S2_RX_DATA)");
  Serial.println("  INMP441 SCK  -> Teensy Pin 13 (I2S2_RX_BCLK)");
  Serial.println("  INMP441 WS   -> Teensy Pin 11 (I2S2_RX_SYNC)");
  Serial.println("  INMP441 VCC  -> 3.3V");
  Serial.println("  INMP441 GND  -> GND");
  Serial.println("  INMP441 L/R  -> GND (left channel)");
  Serial.println();
  Serial.println("Checklist:");
  Serial.println("  [ ] USB Type set to 'Audio' in Arduino IDE");
  Serial.println("  [ ] All wires connected firmly");
  Serial.println("  [ ] INMP441 powered (3.3V)");
  Serial.println("  [ ] L/R pin connected to GND");
  Serial.println();
  Serial.println("Monitoring audio input...");
  Serial.println("=================================");
}

void loop() {
  static unsigned long lastCheck = 0;
  static int noAudioCount = 0;
  
  if (millis() - lastCheck > 500) {
    lastCheck = millis();
    
    if (peak.available()) {
      float level = peak.read();
      
      if (level > 0.01) {
        noAudioCount = 0;
        Serial.print("✓✓✓ AUDIO DETECTED! Level: ");
        Serial.println(level, 4);
      } else {
        noAudioCount++;
        if (noAudioCount % 10 == 0) {
          Serial.print("⚠ No audio detected for ");
          Serial.print(noAudioCount / 2);
          Serial.println(" seconds");
          Serial.println("  Check: Wiring, 3.3V power, L/R->GND");
        }
      }
    }
    
    // Print system stats every 5 seconds
    static int statCounter = 0;
    statCounter++;
    if (statCounter >= 10) {
      statCounter = 0;
      Serial.print("System: CPU=");
      Serial.print(AudioProcessorUsage());
      Serial.print("% | Mem=");
      Serial.print(AudioMemoryUsage());
      Serial.print("/");
      Serial.println(AudioMemoryUsageMax());
    }
  }
}