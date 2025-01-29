#ifndef MUSIC_H
#define MUSIC_H
#include <stdint.h>

#include "flash.h"

extern volatile uint8_t read_next_code, is_playing;
extern volatile uint8_t should_stop;
extern FileReader sheet_reader;

void parse_music_code(char* music_code);

void music_init(uint8_t sheet_idx);

void music_play(void);

void music_pause(void);

void music_stop(void);

#endif