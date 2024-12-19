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
        if (strcmp(filename, available_files[i].name) == 0) {
            reader->file = &available_files[i];
            reader->is_open = 1;
            reader->position = 0;
            return 0; // File opened
        }
    }

    return -2; // File not found
}

int16_t read_chunk(FileReader* reader, char* buffer, uint8_t buffer_size) {
    if (!reader->is_open || !reader->file) {
        return -1; // Nothing to read
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
        return -1; // Nothing to read
    }

    // Calculate remaining characters to read
    uint16_t remaining = reader->file->size - reader->position;
    uint16_t to_read = (remaining < buffer_size) ? remaining : buffer_size;

    // Reached end of file
    if (to_read == 0) {
        return 0;
    }

    // Initialize newline offset at available chars to read by default
    uint8_t newline_offset = to_read;

    // Search for newline
    const char* data = reader->file->data; // Prevents writing 'reader->file->data' all the time
    uint8_t found_newline_flag = 0;
    for (uint8_t i = 0; i < to_read; i++) {
        if (pgm_read_byte(&(data[reader->position + i])) == '\n') {
            newline_offset = i;
            found_newline_flag = 1;
            break;
        }
    }

    // Copy line to buffer
    memcpy_P(buffer, data + reader->position, newline_offset);

    // Update position
    reader->position += (found_newline_flag) ? newline_offset + 1 : newline_offset;

    return newline_offset;
}

uint8_t is_eof(FileReader* reader) {
    uint8_t is_closed = !reader->is_open;
    uint8_t is_file_null = !reader->file;
    uint8_t is_position_at_end = reader->position >= reader->file->size;

    return is_closed || is_file_null || is_position_at_end;
}

void close_file(FileReader* reader) {
    reader->file = NULL;
    reader->is_open = 0;
    reader->position = 0;
}
