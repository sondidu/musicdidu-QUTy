#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

#include "buttons.h"
#include "display.h"
#include "macros/music_macros.h"

/**
 * Initialises TCB0 to generate an interrupt based on
 * BPM, PPQN, subdivisions per tick.
 * 
 * @param bpm Beats per minute
 * @warning Disables global interrupts.
 */
void tcb0_init(uint8_t bpm) {
    cli();
    TCB0.CCMP = (double) 60 / bpm / PPQN / SUBDIVS_PER_TICK * CLK_FREQ;
    TCB0.CNT = 0; // Resetting CNT as this function may be called multiple times.
    TCB0.CTRLB = TCB_CNTMODE_INT_gc;
    TCB0.INTCTRL = TCB_CAPT_bm;
    TCB0.CTRLA = TCB_ENABLE_bm;
}

/**
 * Initialises TCB1 to generate an interrupt every 5ms.
 * This TCB is used for button debouncing and display
 * multiplexing.
 *
 */
void tcb1_init(void) {
    TCB1.CCMP = 16667; // 5ms period
    TCB1.CTRLB = TCB_CNTMODE_INT_gc;
    TCB1.INTCTRL = TCB_CAPT_bm;
    TCB1.CTRLA = TCB_ENABLE_bm;
}

/**
 * Debounce buttons and display multiplex every 5ms.
 * 
 */
ISR(TCB1_INT_vect) {
    buttons_debounce();
    display_multiplex();

    TCB1.INTFLAGS = TCB_CAPT_bm; // Acknowledge interrupt
}