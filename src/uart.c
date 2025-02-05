#include <avr/io.h>
#include <stdio.h>
#include "uart.h"

static FILE stdout_redirected = FDEV_SETUP_STREAM(uart_write, NULL, _FDEV_SETUP_WRITE);

/**
 * Transmits a character via UART.
 * 
 * @param c The character to be transmitted.
 * @param stream The pointer to a FILE object where the character is to be written.
 * @return The character that is transmitted.
 */
int uart_write(char c, FILE *stream) {
    while ( !(USART0.STATUS & USART_DREIF_bm));
    USART0.TXDATAL = c;
    return c;
}

/**
 * Initialises USART to 9600-8-N-1 and redirects stdout.
 *
 * @warning Enables UART TX (PB2) as output, UART RX (PB3) as input.
 */
void uart_init(void) {
    PORTB.DIRSET = PIN2_bm;
    PORTB.DIRCLR = PIN3_bm;
    USART0.BAUD = 1389;
    USART0.CTRLB = USART_TXEN_bm | USART_RXEN_bm;
    stdout = &stdout_redirected;
}