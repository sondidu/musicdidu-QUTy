#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

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

void display_raw(uint8_t left, uint8_t right);