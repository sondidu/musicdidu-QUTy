#ifndef MUSIC_H
#define MUSIC_H
#include <stdint.h>

#include "flash.h"

extern uint8_t read_next_code, fermata, is_playing;
extern uint8_t next_octave, next_tsig_top, next_tsig_bottom;
extern uint16_t next_ticks_play, next_ticks_break, next_note_per, next_bpm_per;
extern uint16_t anacrusis_ticks;

extern FileReader sheet_reader;

void parse_music_code(char* music_code);

void music_init(uint8_t sheet_idx);

void music_play(void);

void music_pause(void);

void music_stop(void);

#endif