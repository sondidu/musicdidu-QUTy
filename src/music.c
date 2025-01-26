#include <avr/io.h>
#include <avr/interrupt.h>

#include "buzzer.h"
#include "flash.h"
#include "macros/music_macros.h"

uint8_t read_next_note, fermata, is_playing = 0;

uint8_t tsig_top, tsig_bottom;
uint8_t next_octave, next_tsig_top, next_tsig_bottom;

uint16_t ticks_play, ticks_break;
uint16_t next_ticks_play, next_ticks_break, next_note_per, next_bpm_per;

uint16_t anacrusis_ticks;

FileReader sheet_reader;

void music_init(uint8_t sheet_idx) {

}

void music_play(void) {
}

void music_pause(void) {
}

void music_stop(void) {

}

void parse_music_code(char* music_code) {

}

ISR(TCB0_INT_vect) {

}