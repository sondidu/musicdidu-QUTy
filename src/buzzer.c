#include <avr/io.h>

#include "buzzer.h"

void buzzer_init(void) {
    PORTB.DIRSET = PIN0_bm;
    TCA0.SINGLE.PER = 0; // Initially silent
    TCA0.SINGLE.CMP0 = 0;
    TCA0.SINGLE.CTRLA = TCA_SINGLE_CLKSEL_DIV4_gc; // Prescaler 4 to cover all 8 octaves
    TCA0.SINGLE.CTRLB = TCA_SINGLE_WGMODE_SINGLESLOPE_gc | TCA_SINGLE_CMP0_bm;
    TCA0.SINGLE.CTRLA |= TCA_SINGLE_ENABLE_bm;
}

void buzzer_note(Note note, uint8_t octave) {
    // To be implemented...
}

/**
 * Silences the buzzer.
 *
 */
void buzzer_silent(void) {
    TCA0.SINGLE.CMP0BUF = 0; // 0% duty cycle
}