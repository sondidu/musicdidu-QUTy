#ifndef DISPLAY_H
#define DISPLAY_H

#include <stdint.h>

void display_init(void);

void display_raw(uint8_t left, uint8_t right);

void display_off(void);

void display_num(uint16_t num);

void display_dp_side(uint8_t side);

void display_dp_on(void);

void display_dp_off(void);

void display_multiplex(void);

#endif
