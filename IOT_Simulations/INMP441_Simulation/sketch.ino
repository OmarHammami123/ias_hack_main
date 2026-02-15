#include <Arduino.h>
#include <driver/i2s.h>
#include <math.h>

#define I2S_PORT I2S_NUM_0

static const int PIN_BCLK = 26; // SCK
static const int PIN_WS   = 25; // WS/LRCLK
static const int PIN_SD   = 33; // SD input

static const int SAMPLE_RATE = 16000;
static const int FRAMES = 256; // stereo frames per read
static int32_t i2sBuf[FRAMES * 2];

static inline int32_t sat24(int64_t v) {
  if (v >  8388607) return  8388607;
  if (v < -8388608) return -8388608;
  return (int32_t)v;
}

void setupI2S() {
  i2s_config_t cfg = {};
  cfg.mode = (i2s_mode_t)(I2S_MODE_MASTER | I2S_MODE_RX);
  cfg.sample_rate = SAMPLE_RATE;
  cfg.bits_per_sample = I2S_BITS_PER_SAMPLE_32BIT;
  cfg.channel_format = I2S_CHANNEL_FMT_RIGHT_LEFT; // interleaved stereo
  cfg.communication_format = I2S_COMM_FORMAT_STAND_I2S;
  cfg.intr_alloc_flags = ESP_INTR_FLAG_LEVEL1;
  cfg.dma_buf_count = 8;
  cfg.dma_buf_len = 64;
  cfg.use_apll = false;
  cfg.tx_desc_auto_clear = false;
  cfg.fixed_mclk = 0;

  i2s_pin_config_t pins = {};
  pins.bck_io_num = PIN_BCLK;
  pins.ws_io_num = PIN_WS;
  pins.data_out_num = I2S_PIN_NO_CHANGE;
  pins.data_in_num = PIN_SD;

  i2s_driver_install(I2S_PORT, &cfg, 0, NULL);
  i2s_set_pin(I2S_PORT, &pins);
  i2s_zero_dma_buffer(I2S_PORT);
}

void setup() {
  Serial.begin(115200);
  delay(300);
  setupI2S();

  // Plotter hint
  Serial.println("# chA,chB,mix");
}

void loop() {
  size_t bytesRead = 0;
  esp_err_t err = i2s_read(I2S_PORT, i2sBuf, sizeof(i2sBuf), &bytesRead, portMAX_DELAY);
  if (err != ESP_OK || bytesRead == 0) {
    Serial.println("0,0,0");
    delay(60);
    return;
  }

  int words = bytesRead / sizeof(int32_t);
  int frames = words / 2;
  if (frames <= 0) return;

  double ssA = 0.0, ssB = 0.0, ssM = 0.0;

  for (int i = 0; i < frames; i++) {
    // Interleaved words: channel A then channel B (order can vary by stack)
    int32_t chA = (int32_t)(i2sBuf[2 * i] >> 8);      // 24-bit signed
    int32_t chB = (int32_t)(i2sBuf[2 * i + 1] >> 8);  // 24-bit signed

    int32_t mix = sat24((int64_t)chA + (int64_t)chB);

    ssA += (double)chA * (double)chA;
    ssB += (double)chB * (double)chB;
    ssM += (double)mix * (double)mix;
  }

  double rmsA = sqrt(ssA / frames);
  double rmsB = sqrt(ssB / frames);
  double rmsM = sqrt(ssM / frames);

  // CSV for Wokwi plotter (3 lines)
  Serial.printf("%.0f,%.0f,%.0f\n", rmsA, rmsB, rmsM);

  delay(60);
}
