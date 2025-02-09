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
uint8_t beats_per_bar, ticks_per_beat;
uint8_t next_octave, next_beats_per_bar, next_ticks_per_beat;

// Tick-playing variables
uint16_t ticks_play, ticks_rest;
uint16_t next_ticks_play, next_ticks_rest, next_note_per, next_bpm_per;

// Fermata and anacrusis
uint8_t next_fermata;
volatile uint8_t fermata;
volatile uint16_t anacrusis_ticks;

// Flags
volatile uint8_t read_next_code, is_playing = 0;
volatile uint8_t should_stop;

// Tick, beat, and bar counting variables
uint16_t tick_count, beat_counter, beat_count, bar_counter, bar_count;

// Decimal Point variables
static uint8_t dp_left, dp_right;

// Last playing note variables (for pause/play)
uint16_t last_playing_per = 0, last_playing_cmp = 0;

FileReader sheet_reader; // Current sheet

/**
 * Parses a given music code string.
 * Music code is formatted to be either a note,
 * fermata-note, rest, bpm, time signature, or
 * anacrusis.
 * @param music_code The music code string.
 */
void parse_music_code(char* music_code) {
    switch (music_code[0]) {
        case PREFIX_ANACRUSIS: {
            sscanf(music_code + 1, "%u", &anacrusis_ticks);
            read_next_code = 1;
            break;
        }
        case PREFIX_BPM: {
            sscanf(music_code + 1, "%u", &next_bpm_per);

            // Calculate BPM's period
            read_next_code = 1;
            break;
        }
        case PREFIX_REST: {
            sscanf(music_code + 1, "%u", &next_ticks_rest);
            next_ticks_play = 0;
            next_note_per = 0;
            read_next_code = 0;
            break;
        }
        case PREFIX_TIME_SIGNATURE: {
            sscanf(music_code + 1, "%hhu/%hhu", &next_beats_per_bar, &next_ticks_per_beat);
            next_ticks_per_beat = PPQN * 4 / next_ticks_per_beat; // Converting to ticks
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
            sscanf(note_str, "%u%c%1hhu%u", &next_ticks_play, &note_char, &next_octave, &next_ticks_rest);

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

/**
 * Initializes music before playing, given a sheet index.
 *
 * @param sheet_idx Index of `available_files` in `data.c`.
 */
void music_init(uint8_t sheet_idx) {
    reader_init(&sheet_reader);
    open_file(&sheet_reader, sheet_idx);

    // Reset all variables
    beats_per_bar = 0, ticks_per_beat = 0;
    next_octave = 0, next_beats_per_bar = 0, next_ticks_per_beat = 0;
    ticks_play = 0, ticks_rest = 0;
    next_ticks_play = 0, next_ticks_rest = 0, next_note_per = 0, next_bpm_per = 0;
    fermata = 0, next_fermata = 0, anacrusis_ticks = 0;
    is_playing = 0, should_stop = 0;
    tick_count = 0;
    beat_counter = 0, beat_count = 0, bar_counter = 0, bar_count = 0;
    dp_left = DP_INITIAL_VAL_LEFT, dp_right = DP_INITIAL_VAL_RIGHT;

    do {
        char word[10];
        uint8_t word_len = read_word(&sheet_reader, word, sizeof(word));

        if (!word_len)
            break;

        parse_music_code(word); // Updates `read_next_code`
    } while (read_next_code);

    // Handle time signature
    if (next_beats_per_bar || next_ticks_per_beat) {
        beats_per_bar = next_beats_per_bar;
        ticks_per_beat = next_ticks_per_beat;
        next_beats_per_bar = 0;
        next_ticks_per_beat = 0;
    }

    // Handle bpm
    if (next_bpm_per) {
        tcb0_init(next_bpm_per);
        next_bpm_per = 0;
    }
}

/**
 * Plays music.
 *
 */
void music_play(void) {
    is_playing = 1;

    // Replay last playing note if any
    if (last_playing_per && last_playing_cmp) {
        TCA0.SINGLE.PERBUF = last_playing_per;
        TCA0.SINGLE.CMP0BUF = last_playing_cmp;
        last_playing_per = 0;
        last_playing_cmp = 0;
    }

    tcb0_start();
}

/**
 * Pauses music.
 *
 */
void music_pause(void) {
    is_playing = 0;

    // Save last playing note
    last_playing_per = TCA0.SINGLE.PER;
    last_playing_cmp = TCA0.SINGLE.CMP0;

    buzzer_silent();
    tcb0_stop();
}

/**
 * Stops music.
 * Closes the file, silences the buzzer.
 *
 */
void music_stop(void) {
    music_pause();
    buzzer_silent();
    close_file(&sheet_reader);
}

/**
 * ISR that handles music playing every tick.
 * A tick is every 1/24th a beat.
 *
 */
ISR(TCB0_INT_vect) {
    if (!is_playing) {
        // Exit early if not playing
        TCB0.INTFLAGS = TCB_CAPT_bm;
        return;
    }

    // Decrement anacrusis ticks
    if (anacrusis_ticks && !--anacrusis_ticks) {
        beat_counter = 0;
        bar_counter = 0;
        dp_left = DP_INITIAL_VAL_LEFT;
        dp_right = DP_INITIAL_VAL_RIGHT;
    }

    // Calculate bars, beats and ticks
    tick_count++;
    if (!fermata || (fermata && (tick_count & 1))) {
        // Increment beat at 0
        if (beat_counter == 0) {
            beat_count++;
            display_dp_sides(dp_left, dp_right);
            dp_left = !dp_left;
            dp_right = !dp_right;

            // Increment bar at 0
            if (bar_counter == 0) {
                display_num(++bar_count);
            }
        } else if (beat_counter == (ticks_per_beat >> 1)) {
            // Turn off DP once half a beat passes
            display_dp_sides(0, 0);
        }

        // Cycle respective counters
        if (++beat_counter == ticks_per_beat) {
            beat_counter = 0;

            if (++bar_counter == beats_per_bar) {
                bar_counter = 0;

                // Reset DP variables to begin next bar
                dp_left = DP_INITIAL_VAL_LEFT;
                dp_right = DP_INITIAL_VAL_RIGHT;
            }
        }
    }

    // Process tick for current note
    if (ticks_play) {
        if (!--ticks_play && ticks_rest)
            buzzer_silent();
    } else if (ticks_rest) {
        ticks_rest--;
    }

    if (!ticks_play && !ticks_rest) {
        // Ticks for next note
        ticks_play = next_ticks_play;
        ticks_rest = next_ticks_rest;
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

        if (next_beats_per_bar || next_ticks_per_beat) {
            beats_per_bar = next_beats_per_bar;
            ticks_per_beat = next_ticks_per_beat;
            next_beats_per_bar = next_ticks_per_beat = 0;
        }

        if (should_stop) {
            music_stop();
            TCB0.INTFLAGS = TCB_CAPT_bm;
            return;
        }
    }

    TCB0.INTFLAGS = TCB_CAPT_bm; // Acknowledge interrupt
}