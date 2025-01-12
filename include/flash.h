#ifndef FLASH_H
#define FLASH_H

#include <stdint.h>

#include "macros/flash_macros.h"

typedef struct {
    const char* data;
    const char* name;
    const uint16_t size;
} FlashFile;

typedef struct {
    const FlashFile* file;
    uint8_t is_open;
    int16_t position;

    char buffer[FILE_READER_BUFFER_SIZE];
    uint8_t buffer_position;
    uint8_t buffer_available;
} FileReader;

void reader_init(FileReader* reader);

int8_t open_file(FileReader* reader, const char* filename);

int16_t read_chunk(FileReader* reader);

int8_t read_word(FileReader* reader, char* word, uint8_t word_size);

uint8_t is_eof(FileReader* reader);

void close_file(FileReader* reader);

#endif
