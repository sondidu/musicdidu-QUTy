#ifndef MUSIC_H
#define MUSIC_H
#include <stdint.h>

#include "flash.h"

extern uint8_t read_next_code, is_playing;
extern FileReader sheet_reader;

void parse_music_code(char* music_code);

void music_init(uint8_t sheet_idx);

void music_play(void);

void music_pause(void);

void music_stop(void);

#endif