#include <avr/io.h>
#include <stdint.h>

#include "buttons.h"

static volatile uint8_t pb_falling, pb_rising;

/**
 * Enables pull-up resistors for all the buttons. (PA4-PA7)
 *
 */
void buttons_init(void) {
    PORTA.PIN4CTRL = PORT_PULLUPEN_bm;
    PORTA.PIN5CTRL = PORT_PULLUPEN_bm;
    PORTA.PIN6CTRL = PORT_PULLUPEN_bm;
    PORTA.PIN7CTRL = PORT_PULLUPEN_bm;
}

/**
 * Returns the falling state of push buttons in the
 * form of an unsigned 8-bit integer.
 *
 */
uint8_t get_presses(void) {
    return pb_falling;
}

/**
 * Returns the rising state of push buttons in the
 * form of an unsigned 8-bit integer.
 *
 */
uint8_t get_releases(void) {
    return pb_rising;
}

/**
 * Debounces push buttons and updates the rising
 * and falling flags.
 * 
 */
void buttons_debounce(void) {
    // Push button states
    static uint8_t pb_current = 0xFF, pb_previous = 0xFF;

    // Vertical counters
    static uint8_t counter0 = 0, counter1 = 0;

    // Record sample and changed
    uint8_t pb_sample = PORTA.IN;
    uint8_t pb_changed = pb_sample ^ pb_current;

    // Increment counters while changed, else reset
    counter1 = (counter1 ^ counter0) & pb_changed;
    counter0 = ~counter0 & pb_changed;

    // Update previous iteration
    pb_previous = pb_current;

    // Record those that are stable for 3 samples
    pb_current ^= counter0 & counter1;

    // Get falling and rising edges
    pb_falling = pb_previous & ~pb_current;
    pb_rising = ~pb_previous & pb_current;
}