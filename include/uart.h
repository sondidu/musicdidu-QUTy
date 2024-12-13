#ifndef UART_H
#define UART_H

#include <stdio.h>

int uart_write(char c, FILE *stream);

void uart_init(void);

#endif
