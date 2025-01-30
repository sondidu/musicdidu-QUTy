#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdio.h>

#include "buzzer.h"
#include "display.h"
#include "flash.h"
#include "macros/music_macros.h"
#include "music.h"
#include "timers.h"

// Time signature variables
uint8_t tsig_top, tsig_bottom;
uint8_t next_octave, next_tsig_top, next_tsig_bottom;

// Tick-playing variables
uint16_t ticks_play, ticks_break;
uint16_t next_ticks_play, next_ticks_break, next_note_per, next_bpm_per;

// Fermata and anacrusis
uint8_t next_fermata;
volatile uint8_t fermata;
volatile uint16_t anacrusis_ticks;

// Flags
volatile uint8_t read_next_code, is_playing = 0;
volatile uint8_t should_stop;

// Tick, beat, and bar counting variables
uint16_t tick_count, beat_counter, beat_count, bar_counter, bar_count;

FileReader sheet_reader; // Current sheet

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
            next_note_per = 0;
            read_next_code = 0;
            break;
        }
        case PREFIX_TIME_SIGNATURE: {
            sscanf(music_code + 1, "%hhu/%hhu", &next_tsig_top, &next_tsig_bottom);
            next_tsig_bottom = PPQN * 4 / next_tsig_bottom;
            read_next_code = 1;
            break;
        }
        default: {
            char* note_str = music_code;
            if (music_code[0] == PREFIX_FERMATA) {
                note_str++;
                next_fermata = 1;
            } else {
                next_fermata = 0;
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

    // Reset all variables
    tsig_top = 0, tsig_bottom = 0;
    next_octave = 0, next_tsig_top = 0, next_tsig_bottom = 0;
    ticks_play = 0, ticks_break = 0;
    next_ticks_play = 0, next_ticks_break = 0, next_note_per = 0, next_bpm_per = 0;
    fermata = 0, next_fermata = 0, anacrusis_ticks = 0;
    is_playing = 0, should_stop = 0;
    tick_count = 0;
    beat_counter = 0, beat_count = 0, bar_counter = 0, bar_count = 0;

    do {
        char word[10];
        uint8_t word_len = read_word(&sheet_reader, word, sizeof(word));

        if (!word_len)
            break;

        parse_music_code(word); // Updates `read_next_code`
    } while (read_next_code);

    // Handle time signature
    if (next_tsig_top || next_tsig_bottom) {
        tsig_top = next_tsig_top;
        tsig_bottom = next_tsig_bottom;
        next_tsig_top = 0;
        next_tsig_bottom = 0;
    }

    // Handle bpm
    if (next_bpm_per) {
        tcb0_init(next_bpm_per);
        next_bpm_per = 0;
    }

    // Handle notes
    if (next_ticks_play || next_ticks_break) {
        ticks_play = next_ticks_play;
        ticks_break = next_ticks_break;
    }
}

void music_play(void) {
    is_playing = 1;
    display_num(0);
    display_dp_sides(0, 1);
    tcb0_start();
}

void music_pause(void) {
    is_playing = 0;
    tcb0_stop();
}

void music_stop(void) {
    music_pause();
    buzzer_silent();
    close_file(&sheet_reader);
}

ISR(TCB0_INT_vect) {
    if (!is_playing) {
        // Exit early if not playing
        TCB0.INTFLAGS = TCB_CAPT_bm;
        return;
    }

    static uint8_t left_dp = 1, right_dp = 0;

    // Calculate bars, beats and ticks
    tick_count++;
    if (!fermata || (fermata && (tick_count & 1))) {
        // Increment beat at 0
        if (beat_counter == 0) {
            beat_count++;
            display_dp_sides(left_dp, right_dp);
            left_dp = !left_dp;
            right_dp = !right_dp;

            // Increment bar at 0
            if (bar_counter == 0) {
                display_num(++bar_count);
            }
        }

        if (++beat_counter == tsig_bottom) {
            beat_counter = 0;

            if (++bar_counter == tsig_top) {
                bar_counter = 0;
            }
        }
    }

    // Decrement anacrusis ticks
    if (anacrusis_ticks && !--anacrusis_ticks) {
        beat_counter = 0;
        bar_counter = 0;
        left_dp = 1;
        right_dp = 0;
        display_dp_sides(left_dp, right_dp);
        display_num(++bar_count);
    }

    // Process tick for current note
    if (ticks_play) {
        if (!--ticks_play && ticks_break)
            buzzer_silent();
    } else if (ticks_break) {
        ticks_break--;
    }

    if (!ticks_play && !ticks_break) {
        // Ticks for next note
        ticks_play = next_ticks_play;
        ticks_break = next_ticks_break;
        fermata = next_fermata;
        read_next_code = 1;

        if (next_note_per) {
            buzzer_note(next_note_per, next_octave);
        } else {
            buzzer_silent();
        }

        if (next_bpm_per) {
            tcb0_stop();
            tcb0_init(next_bpm_per);
            tcb0_start();
            next_bpm_per = 0;
        }

        if (next_tsig_top || next_tsig_bottom) {
            tsig_top = next_tsig_top;
            tsig_bottom = next_tsig_bottom;
            next_tsig_top = next_tsig_bottom = 0;
        }

        if (should_stop) {
            music_stop();
            TCB0.INTFLAGS = TCB_CAPT_bm;
            return;
        }
    }

    TCB0.INTFLAGS = TCB_CAPT_bm; // Acknowledge interrupt
}