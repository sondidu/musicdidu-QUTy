#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

#include "macros/display_macros.h"

static uint8_t left_raw = DISP_OFF;
static uint8_t right_raw = DISP_OFF;

/**
 * Initialises SPI0 to read and write data in 
 * unbuffered mode and enables interrupt.
 *
 */
static void spi_init(void) {
    SPI0.CTRLA = SPI_MASTER_bm;
    SPI0.CTRLB = SPI_SSD_bm;
    SPI0.INTCTRL = SPI_IE_bm;
    SPI0.CTRLA |= SPI_ENABLE_bm;
}

static void spi_write(uint8_t data) {
    SPI0.DATA = data;
}

/**
 * Initialises spi (with `spi_init()`) and display-related
 * peripherals.
 *
 * @warning Enables DISP LATCH (PA1) as output.
 */
void display_init(void) {
    PORTC.DIRSET = PIN0_bm | PIN2_bm;
    PORTA.DIRSET = PIN1_bm;
    PORTMUX.SPIROUTEA = PORTMUX_SPI0_ALT1_gc; // Reroutes to the correct ports for QUTy
    spi_init();
}

/**
 * Displays raw data of the left and right
 * side of the 7-segment display.
 * 
 * @note Left and right values are always ensured to be at their respective sides.
 * @param left Raw left data.
 * @param right Raw right data.
 */
void display_raw(uint8_t left, uint8_t right) {
    left_raw = left | DISP_FORCE_LEFT;
    right_raw = right & DISP_FORCE_RIGHT;
}

/**
 * Turns the display off.
 *
 */
void display_off(void) {
    display_raw(DISP_OFF, DISP_OFF);
}

/**
 * Displays the last two digits of an integer.
 *
 * @note If the number is a single digit, then the left side is off.
 * @param num The number to be displayed.
 */
void display_num(uint16_t num) {
    const uint8_t digit_map[] = {
        DISP_DIGIT_ZERO,
        DISP_DIGIT_ONE,
        DISP_DIGIT_TWO,
        DISP_DIGIT_THREE,
        DISP_DIGIT_FOUR,
        DISP_DIGIT_FIVE,
        DISP_DIGIT_SIX,
        DISP_DIGIT_SEVEN,
        DISP_DIGIT_EIGHT,
        DISP_DIGIT_NINE
    };

    uint8_t last_two_digits = num % 100;
    uint8_t left = (num < 10) ? DISP_OFF : digit_map[last_two_digits / 10];
    uint8_t right = digit_map[last_two_digits % 10];
    display_raw(left, right);
}

/**
 * Alternates writing left and right raw data to the SPI.
 *
 */
void display_multiplex(void) {
    static uint8_t which_side = 0;

    uint8_t raw_data = which_side ? left_raw : right_raw;

    which_side = !which_side;

    spi_write(raw_data);
}

/**
 * Drives DISP LATCH high and low after every complete write
 * to the SPI.
 *
 */
ISR(SPI0_INT_vect) {
    PORTA.OUTSET = PIN1_bm;
    PORTA.OUTCLR = PIN1_bm;
    SPI0.INTFLAGS = SPI_IF_bm; // Acknowledge interrupt
}