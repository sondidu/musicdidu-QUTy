#include <avr/pgmspace.h>
#include <stdint.h>
#include <stdio.h>
#include <string.h>

#include "data.h"
#include "flash.h"

void reader_init(FileReader* reader) {
   reader->file = NULL;
   reader->is_open = 0;
   reader->position = 0;
}

int8_t open_file(FileReader* reader, const char* filename) {
    if (reader->is_open) {
        return -1; // File already opened
    }

    for (uint8_t i = 0; i < available_files_count; i++) {
        const FlashFile current_file = available_files[i];
        if (strcmp(filename, current_file.name) == 0) {
            reader->file = &current_file;
            reader->is_open = 1;
            reader->position = 0;
            return 0; // File opened
        }
    }

    return -2; // File not found
}

int16_t read_chunk(FileReader* reader, char* buffer, uint8_t buffer_size) {
    if (!reader->is_open || !reader->file) {
        return -1; // There's nothing to read
    }

    // Calculate remaining characers to read
    uint16_t remaining = reader->file->size - reader->position;
    uint16_t to_read = (remaining < buffer_size) ? remaining : buffer_size;

    // Reached end of file
    if (to_read == 0) {
        return 0;
    }

    // Copy chunk to buffer
    memcpy_P(buffer, reader->file->data + reader->position, to_read);

    // Update position
    reader->position += to_read;

    return to_read;
}

int16_t read_line(FileReader* reader, char* buffer, uint8_t buffer_size) {
    if (!reader->is_open || !reader->file) {
        return -1; // There's nothing to read
    }

    // Calculate remaining characters
    uint16_t remaining = reader->file->size - reader->position;
    uint16_t to_read = (remaining < buffer_size) ? remaining : buffer_size;

    uint8_t newline_offset;
    uint8_t i;

    const char* data = reader->file->data;
    for (i = 0; i < to_read; i++) {
        if (data[reader->position + i] == '\n') {
            newline_offset = i;
            break;
        }
    }

    // Newline char not found
    if (i == to_read) {
        newline_offset = to_read;
    }

    // Copy line to buffer
    memcpy_P(buffer, reader->file->data + reader->position, newline_offset);

    // Update position
    reader->position += (data[newline_offset] == '\n') ? newline_offset + 1 : newline_offset;

    printf("position: %u\n", reader->position);
    return newline_offset;
}

uint8_t is_eof(FileReader* reader) {
    // File is already closed
    if (!reader->is_open || !reader->file) {
        return 1;
    }

    return (reader->position >= reader->file->size);
}

void close_file(FileReader* reader) {
    reader->file = NULL;
    reader->is_open = 0;
    reader->position = 0;
}
