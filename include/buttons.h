#ifndef BUTTONS_H
#define BUTTONS_H

#include <stdint.h>

void buttons_init(void);

uint8_t get_presses(void);

uint8_t get_releases(void);

void buttons_debounce(void);

#endif
