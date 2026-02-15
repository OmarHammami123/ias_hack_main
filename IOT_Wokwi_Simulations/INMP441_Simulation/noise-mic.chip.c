#include "wokwi-api.h"
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>

#define MAX_24BIT 8388607.0f

typedef struct {
  pin_t sck, ws, sd, lr;
  uint32_t level_attr, spike_attr;
  uint32_t last_ws;
  uint8_t bit_index;
  uint32_t sample_word;
  bool driving;
} chip_state_t;

static inline int32_t clamp24(int64_t v) {
  if (v >  8388607) return  8388607;
  if (v < -8388608) return -8388608;
  return (int32_t)v;
}

static inline uint32_t pack24_to_i2s32(int32_t s24) {
  return ((uint32_t)(s24 & 0xFFFFFF)) << 8;
}

static inline bool slot_is_active(chip_state_t *chip, uint32_t ws_now) {
  bool left = (pin_read(chip->lr) == LOW);
  return left ? (ws_now == LOW) : (ws_now == HIGH);
}

static uint32_t gen_noise_word(chip_state_t *chip) {
  float level = attr_read_float(chip->level_attr);     // white-noise level
  float spike = attr_read_float(chip->spike_attr);     // impulsive bursts

  if (level < 0) level = 0; if (level > 1) level = 1;
  if (spike < 0) spike = 0; if (spike > 1) spike = 1;

  float rnd = ((float)rand() / (float)RAND_MAX) * 2.0f - 1.0f;
  float x = level * rnd;

  // occasional burst spikes
  float p = 0.002f + spike * 0.05f;
  if (((float)rand() / (float)RAND_MAX) < p) {
    float sign = (rand() & 1) ? 1.0f : -1.0f;
    float mag = level * (0.6f + 0.4f * ((float)rand() / (float)RAND_MAX));
    x += sign * mag;
  }

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
      chip->sample_word = gen_noise_word(chip);
    }
  }

  bool active = slot_is_active(chip, ws_now);
  if (active != chip->driving) {
    chip->driving = active;
    pin_mode(chip->sd, chip->driving ? OUTPUT_LOW : INPUT); // tri-state when inactive
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
  chip->sd  = pin_init("SD", INPUT);            // start in Hi-Z
  chip->lr  = pin_init("LR", INPUT_PULLDOWN);   // default LOW

  chip->level_attr = attr_init_float("level", 0.20f);
  chip->spike_attr = attr_init_float("spikiness", 0.15f);

  chip->last_ws = pin_read(chip->ws);
  chip->bit_index = 0;
  chip->sample_word = 0;
  chip->driving = false;

  const pin_watch_config_t watch = {
    .edge = FALLING,
    .pin_change = on_sck_falling,
    .user_data = chip
  };
  pin_watch(chip->sck, &watch);
}
