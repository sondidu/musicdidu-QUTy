#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdio.h>

#include "buzzer.h"
#include "flash.h"
#include "macros/music_macros.h"
#include "music.h"

uint8_t read_next_code, fermata, is_playing = 0;

uint8_t tsig_top, tsig_bottom;
uint8_t next_octave, next_tsig_top, next_tsig_bottom;

uint16_t ticks_play, ticks_break;
uint16_t next_ticks_play, next_ticks_break, next_note_per, next_bpm_per;

uint16_t anacrusis_ticks;

FileReader sheet_reader;

void parse_music_code(char* music_code) {
    switch (music_code[0]) {
        case PREFIX_ANACRUSIS: {
            sscanf(music_code + 1, "%u", &anacrusis_ticks);
            read_next_code = 1;
            break;
        }
        case PREFIX_BPM: {
            uint8_t next_bpm = 0;
            sscanf(music_code + 1, "%hhu", &next_bpm);

            // Calculate BPM's period
            next_bpm_per = (uint32_t) FREQ_CLK_DIV2 * 60 / next_bpm / PPQN;
            read_next_code = 1;
            break;
        }
        case PREFIX_BREAK: {
            sscanf(music_code + 1, "%u", &next_ticks_break);
            read_next_code = 0;
            break;
        }
        case PREFIX_TIME_SIGNATURE: {
            sscanf(music_code + 1, "%hhu/%hhu", &next_tsig_top, &next_tsig_bottom);
            next_tsig_bottom = 32 / next_tsig_bottom;
            read_next_code = 1;
            break;
        }
        default: {
            char* note_str = music_code;
            if (music_code[0] == PREFIX_FERMATA) {
                note_str++;
                fermata = 1;
            }

            char note_char;
            sscanf(note_str, "%u%c%1hhu%u", &next_ticks_play, &note_char, &next_octave, &next_ticks_break);

            static const uint16_t note_pers[] = {
                NOTE_PER_A, NOTE_PER_A_SHARP, NOTE_PER_A_FLAT,
                NOTE_PER_B, NOTE_PER_B_SHARP, NOTE_PER_B_FLAT,
                NOTE_PER_C, NOTE_PER_C_SHARP, NOTE_PER_C_FLAT,
                NOTE_PER_D, NOTE_PER_D_SHARP, NOTE_PER_D_FLAT,
                NOTE_PER_E, NOTE_PER_E_SHARP, NOTE_PER_E_FLAT,
                NOTE_PER_F, NOTE_PER_F_SHARP, NOTE_PER_F_FLAT,
                NOTE_PER_G, NOTE_PER_G_SHARP, NOTE_PER_G_FLAT
            };

            next_note_per = note_pers[note_char - NOTE_CHAR_START];
            read_next_code = 0;
            break;
        }
    }
}

void music_init(uint8_t sheet_idx) {
    reader_init(&sheet_reader);
    open_file(&sheet_reader, sheet_idx);
    is_playing = 0;

    char word[10];

    while(1) {
        uint8_t word_len = read_word(&sheet_reader, word, sizeof(word));

        if (!word_len)
            break;

        parse_music_code(word);

        // Stop at first note music code
        if (word[0] != PREFIX_ANACRUSIS &&
            word[0] != PREFIX_BPM &&
            word[0] != PREFIX_TIME_SIGNATURE) {
                break;
            }
    }
}

void music_play(void) {
}

void music_pause(void) {
}

void music_stop(void) {

}

ISR(TCB0_INT_vect) {

}