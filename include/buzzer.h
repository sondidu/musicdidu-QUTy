#ifndef BUZZER_H
#define BUZZER_H

#include <stdint.h>

#include "types/notes.h"

void buzzer_init(void);

void buzzer_note(Note note, uint8_t octave);

void buzzer_silent(void);

#endif
