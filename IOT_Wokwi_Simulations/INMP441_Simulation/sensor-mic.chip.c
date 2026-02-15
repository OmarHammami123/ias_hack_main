#include "wokwi-api.h"
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <math.h>

#define SAMPLE_RATE_HZ 16000.0f
#define MAX_24BIT      8388607.0f
#define TWO_PI         6.28318530718f

typedef struct {
  pin_t sck, ws, sd, lr;
  uint32_t amp_attr, tone_attr, self_noise_attr;
  uint32_t last_ws;
  uint8_t bit_index;
  uint32_t sample_word;
  float phase;
  bool driving;
} chip_state_t;

static inline int32_t clamp24(int64_t v) {
  if (v >  8388607) return  8388607;
  if (v < -8388608) return -8388608;
  return (int32_t)v;
}

static inline uint32_t pack24_to_i2s32(int32_t s24) {
  return ((uint32_t)(s24 & 0xFFFFFF)) << 8; // left-justified 24-bit in 32-bit word
}

static inline bool slot_is_active(chip_state_t *chip, uint32_t ws_now) {
  // LR=LOW => left slot (WS=LOW), LR=HIGH => right slot (WS=HIGH)
  bool left = (pin_read(chip->lr) == LOW);
  return left ? (ws_now == LOW) : (ws_now == HIGH);
}

static uint32_t gen_sensor_word(chip_state_t *chip) {
  float amp = attr_read_float(chip->amp_attr);
  float hz  = attr_read_float(chip->tone_attr);
  float nz  = attr_read_float(chip->self_noise_attr);

  if (amp < 0) amp = 0; if (amp > 1) amp = 1;
  if (hz < 10) hz = 10;
  if (nz < 0) nz = 0; if (nz > 1) nz = 1;

  chip->phase += TWO_PI * (hz / SAMPLE_RATE_HZ);
  if (chip->phase >= TWO_PI) chip->phase -= TWO_PI;

  float sine = sinf(chip->phase);
  float rnd  = ((float)rand() / (float)RAND_MAX) * 2.0f - 1.0f;
  float x    = amp * sine + nz * rnd;

  if (x > 1.0f) x = 1.0f;
  if (x < -1.0f) x = -1.0f;

  int32_t s24 = clamp24((int64_t)(x * MAX_24BIT));
  return pack24_to_i2s32(s24);
}

static void on_sck_falling(void *user_data, pin_t pin, uint32_t value) {
  (void)pin;
  (void)value;

  chip_state_t *chip = (chip_state_t *)user_data;
  uint32_t ws_now = pin_read(chip->ws);

  if (ws_now != chip->last_ws) {
    chip->last_ws = ws_now;
    chip->bit_index = 0;
    if (slot_is_active(chip, ws_now)) {
      chip->sample_word = gen_sensor_word(chip);
    }
  }

  bool active = slot_is_active(chip, ws_now);
  if (active != chip->driving) {
    chip->driving = active;
    // Tri-state SD when inactive (important for shared bus)
    pin_mode(chip->sd, chip->driving ? OUTPUT_LOW : INPUT);
  }

  if (chip->driving) {
    uint32_t bit = (chip->sample_word >> (31 - chip->bit_index)) & 1u;
    pin_write(chip->sd, bit ? HIGH : LOW);
  }

  chip->bit_index++;
  if (chip->bit_index >= 32) chip->bit_index = 0;
}

void chip_init() {
  chip_state_t *chip = malloc(sizeof(chip_state_t));

  chip->sck = pin_init("SCK", INPUT);
  chip->ws  = pin_init("WS", INPUT);
  chip->sd  = pin_init("SD", INPUT);             // start in Hi-Z
  chip->lr  = pin_init("LR", INPUT_PULLDOWN);    // default LOW

  chip->amp_attr        = attr_init_float("amplitude", 0.70f);
  chip->tone_attr       = attr_init_float("toneHz", 380.0f);
  chip->self_noise_attr = attr_init_float("selfNoise", 0.02f);

  chip->last_ws = pin_read(chip->ws);
  chip->bit_index = 0;
  chip->sample_word = 0;
  chip->phase = 0.0f;
  chip->driving = false;

  const pin_watch_config_t watch = {
    .edge = FALLING,
    .pin_change = on_sck_falling,
    .user_data = chip
  };
  pin_watch(chip->sck, &watch);
}
