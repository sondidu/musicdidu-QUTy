#include <avr/io.h>

#include "buzzer.h"
#include "macros/music_macros.h"

/**
 * Initialises buzzer @ 1.67 MHz (prescaler 2), initially silent.
 *
 * @warning Enables buzzer (PB0) as output.
 */
void buzzer_init(void) {
    PORTB.DIRSET = PIN0_bm;
    TCA0.SINGLE.PER = 0; // Initially silent
    TCA0.SINGLE.CMP0 = 0;
    TCA0.SINGLE.CTRLA = TCA_SINGLE_CLKSEL_DIV2_gc; // Prescaler 2 to cover octave 0 and beyond
    TCA0.SINGLE.CTRLB = TCA_SINGLE_WGMODE_SINGLESLOPE_gc | TCA_SINGLE_CMP0_bm;
    TCA0.SINGLE.CTRLA |= TCA_SINGLE_ENABLE_bm;
}

/**
 * Plays the note.
 * 
 * @param note Note to be played.
 * @param octave At what octave the note to be played.
 */
void buzzer_note(uint16_t note_period, uint8_t octave) {
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