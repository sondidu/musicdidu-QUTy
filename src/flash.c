#include <avr/pgmspace.h>
#include <stdint.h>
#include <string.h>

#include "data.h"
#include "flash.h"
#include "macros/flash_macros.h"

/**
 * Initializes the reader before use.
 *
 * @param reader The address of the reader.
 */
void reader_init(FileReader* reader) {
   reader->file = NULL;
   reader->is_open = 0;
   reader->position = 0;
   reader->buffer_position = 0;
   reader->buffer_available = 0;
}

/**
 * Opens a file given a reader and the filename.
 *
 * @param reader The address of the reader.
 * @param filename The filename.
 * @return int8_t
 */
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

/**
 * Copys a chunk of chars from PROGMEM to the reader's buffer,
 * given a reader.
 *
 * @param reader The address of the reader.
 * @return int16_t The number of chars read.
 */
int16_t read_chunk(FileReader* reader) {
    if (!reader->is_open || !reader->file) {
        return -1; // Nothing to read
    }

    // Calculate remaining characers to read
    uint16_t remaining = reader->file->size - reader->position;
    uint16_t to_read = (remaining < sizeof(reader->buffer)) ? remaining : sizeof(reader->buffer);

    // Reached end of file
    if (to_read == 0) {
        return 0;
    }

    // Copy chunk to buffer
    memcpy_P(reader->buffer, reader->file->data + reader->position, to_read);

    // Update position and buffer variables
    reader->position += to_read;
    reader->buffer_position = 0;
    reader->buffer_available = to_read;

    return to_read;
}

/**
 * Copys the next word from reader to a word buffer,
 * given a reader, word buffer and word buffer's size.
 * 
 * @param reader The address of the reader.
 * @param word_buffer The word buffer to copy to.
 * @param word_buffer_size The size of the word buffer.
 * @return int8_t 
 */
int8_t read_word(FileReader* reader, char* word_buffer, uint8_t word_buffer_size) {
    if (!reader->is_open || !reader->file) {
        return -1; // Nothing to read
    }

    uint8_t word_len = 0;
    uint8_t is_in_word = 0; // To track whether we're currently in a word

    while (word_len < word_buffer_size - 1) { // Minus one for null terminator
        // Refill reader's buffer if no more chars available
        if (reader->buffer_position >= reader->buffer_available) {
            int16_t bytes_read = read_chunk(reader);

            if (bytes_read <= 0) {
                // EOF or error
                break;
            }
        }

        // Get char from reader's buffer
        char c = reader->buffer[reader->buffer_position++];

        // Skip whitespace
        if (c == ' ' || c == '\n') {
            if (is_in_word) {
                // Have found end of word
                break;
            }

            // Haven't found beginning of a word, still skipping whitespaces
            continue;
        }

        word_buffer[word_len++] = c;
        is_in_word = 1;
    }

    word_buffer[word_len] = '\0'; // Null terminate
    return word_len;
}

/**
 * Returns whether it is the end of file.
 *
 * @param reader The address of the reader.
 * @return uint8_t
 */
uint8_t is_eof(FileReader* reader) {
    // File is open
    if (!reader->is_open || !reader->file) {
        return 1;
    }

    // There's still some data in the buffer
    if (reader->buffer_position < reader->buffer_available) {
        return 0;
    }

    // Finally, compare position and file size
    return reader->position >= reader->file->size;
}

/**
 * Closes a file.
 *
 * @param reader The address of the reader.
 */
void close_file(FileReader* reader) {
    reader->file = NULL;
    reader->is_open = 0;
    reader->position = 0;
    reader->buffer_position = 0;
    reader->buffer_available = 0;
}
