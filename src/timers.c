#include <avr/io.h>
#include <avr/interrupt.h>

#include "buttons.h"
#include "display.h"

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