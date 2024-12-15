#ifndef BUZZER_H
#define BUZZER_H

#include <stdint.h>

void buzzer_init(void);

void buzzer_note(uint16_t note_period, uint8_t octave);

void buzzer_silent(void);

#endif
