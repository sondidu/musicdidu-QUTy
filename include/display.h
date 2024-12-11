#include <stdint.h>

static void spi_init(void);

static void spi_write(uint8_t data);

void display_init(void);

void display_raw(uint8_t left, uint8_t right);

void display_off(void);

void display_num(uint16_t num);

void display_multiplex(void);