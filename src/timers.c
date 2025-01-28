#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

#include "buttons.h"
#include "display.h"

/**
 * Initialises TCB0 @1.67 MHz (prescaler 2) to generate an
 * interrupt based on BPM and PPQN.
 *
 * @param ccmp_per The CCMP's period value.
 * @warning Doesn't start immediately.
 */
void tcb0_init(uint16_t ccmp_per) {
    TCB0.CCMP = ccmp_per;
    TCB0.CNT = 0;
    TCB0.CTRLB = TCB_CNTMODE_INT_gc;
    TCB0.INTCTRL = TCB_CAPT_bm;
    TCB0.CTRLA = TCB_CLKSEL_DIV2_gc;
}

/**
 * Enables TCB0 with its current configuration (if any).
 *
 */
void tcb0_start(void) {
    TCB0.CTRLA |= TCB_ENABLE_bm;
}

/**
 * Disables TCB0, leaving everything at its state.
 *
 */
void tcb0_stop(void) {
    TCB0.CTRLA &= ~TCB_ENABLE_bm;
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