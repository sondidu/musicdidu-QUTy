#include <avr/io.h>

#include "buzzer.h"
#include "macros/period_macros.h"

/**
 * Initialises buzzer @ 0.83 MHz (prescaler 4), initially silent.
 *
 * @warning Enables buzzer (PB0) as output.
 */
void buzzer_init(void) {
    PORTB.DIRSET = PIN0_bm;
    TCA0.SINGLE.PER = 0; // Initially silent
    TCA0.SINGLE.CMP0 = 0;
    TCA0.SINGLE.CTRLA = TCA_SINGLE_CLKSEL_DIV4_gc; // Prescaler 4 to cover all 8 octaves
    TCA0.SINGLE.CTRLB = TCA_SINGLE_WGMODE_SINGLESLOPE_gc | TCA_SINGLE_CMP0_bm;
    TCA0.SINGLE.CTRLA |= TCA_SINGLE_ENABLE_bm;
}

/**
 * Plays the note.
 * 
 * @param note Note to be played.
 * @param octave At what octave the note to be played.
 */
void buzzer_note(Note note, uint8_t octave) {
    uint16_t note_period = 0;
    switch (note) {
        case C_FLAT:
            note_period = NOTE_PER_C_FLAT;
            break;
        case C:
            note_period = NOTE_PER_C;
            break;
        case C_SHARP:
            note_period = NOTE_PER_C_SHARP;
            break;
        case D_FLAT:
            note_period = NOTE_PER_D_FLAT;
            break;
        case D:
            note_period = NOTE_PER_D;
            break;
        case D_SHARP:
            note_period = NOTE_PER_D_SHARP;
            break;
        case E_FLAT:
            note_period = NOTE_PER_E_FLAT;
            break;
        case E:
            note_period = NOTE_PER_E;
            break;
        case E_SHARP:
            note_period = NOTE_PER_E_SHARP;
            break;
        case F_FLAT:
            note_period = NOTE_PER_F_FLAT;
            break;
        case F:
            note_period = NOTE_PER_F;
            break;
        case F_SHARP:
            note_period = NOTE_PER_F_SHARP;
            break;
        case G_FLAT:
            note_period = NOTE_PER_G_FLAT;
            break;
        case G:
            note_period = NOTE_PER_G;
            break;
        case G_SHARP:
            note_period = NOTE_PER_G_SHARP;
            break;
        case A_FLAT:
            note_period = NOTE_PER_A_FLAT;
            break;
        case A:
            note_period = NOTE_PER_A;
            break;
        case A_SHARP:
            note_period = NOTE_PER_A_SHARP;
            break;
        case B_FLAT:
            note_period = NOTE_PER_B_FLAT;
            break;
        case B:
            note_period = NOTE_PER_B;
            break;
        case B_SHARP:
            note_period = NOTE_PER_B_SHARP;
            break;
        default:
            note_period = 0; // Silent
            break;
    }

    // Since dealing with periods, to increase a frequency, we decrease the period
    if (octave > OCTAVE_STANDARD) {
        note_period >>= octave - OCTAVE_STANDARD; // Equivalent to divide by 2^(octave - standard)
    } else if (octave < OCTAVE_STANDARD) {
        note_period <<= OCTAVE_STANDARD - octave; // Equivalent to multiply by 2^(standard - octave)
    }

    TCA0.SINGLE.PERBUF = note_period;
    TCA0.SINGLE.CMP0BUF = note_period >> 1; // 50% duty cycle
}

/**
 * Silences the buzzer.
 *
 */
void buzzer_silent(void) {
    TCA0.SINGLE.CMP0BUF = 0; // 0% duty cycle
}