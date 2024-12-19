#ifndef FLASH_H
#define FLASH_H

#include <stdint.h>

typedef struct {
    const char* data;
    const char* name;
    const uint16_t size;
} FlashFile;

typedef struct {
    const FlashFile* file;
    uint8_t is_open;
    int16_t position;
} FileReader;

void reader_init(FileReader* reader);

int8_t open_file(FileReader* reader, const char* filename);

int16_t read_chunk(FileReader* reader, char* buffer, uint8_t buffer_size);

int16_t read_line(FileReader* reader, char* buffer, uint8_t buffer_size);

uint8_t is_eof(FileReader* reader);

void close_file(FileReader* reader);

#endif
