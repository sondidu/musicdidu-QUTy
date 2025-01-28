#ifndef TIMERS_H
#define TIMERS_H

#include <stdint.h>

void tcb0_init(uint16_t ccmp_per);

void tcb0_start(void);

void tcb0_stop(void);

void tcb1_init(void);

#endif
