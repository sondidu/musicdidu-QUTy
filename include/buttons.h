#include <stdint.h>

void buttons_init(void);

uint8_t get_presses(void);

uint8_t get_releases(void);

void debounce_buttons(void);