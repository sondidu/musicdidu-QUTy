#include <avr/io.h>
#include <avr/interrupt.h>
#include <stdint.h>

#include "buttons.h"
#include "buzzer.h"
#include "data.h"
#include "display.h"
#include "flash.h"
#include "music.h"
#include "timers.h"

typedef enum {
    SELECTION_IDLE,
    SELECTION_CHANGE_PRESSED,
    SELECTION_MADE_PRESSED,
    SELECTION_AWAITING_CONFIRMATION,
    SELECTION_CANCEL,
    MUSIC_PLAYING,
    MUSIC_PAUSED_IDLE,
    MUSIC_STOPPING_PRESSED
} state_t;


void inits(void) {
    cli();
    buttons_init();
    buzzer_init();
    tcb1_init();
    display_init();
    sei();
}

int main(void) {
    inits();

    uint8_t file_idx = 0;
    state_t state = SELECTION_IDLE;
    display_num(1);
    display_dp_sides(0, 0);

    while (1) {
        switch (state) {
            case SELECTION_IDLE: {
                uint8_t presses = get_presses();

                if (presses & (PIN4_bm | PIN5_bm)) {
                    // S1 decrements `file_idx`
                    if ((presses & PIN4_bm) && file_idx) {
                        file_idx--;
                    }

                    // S2 increments `file_idx`
                    if ((presses & PIN5_bm) && file_idx < available_files_count - 1) {
                        file_idx++;
                    }

                    display_num(file_idx + 1); // +1 displays the file number (instead of file index)
                    state = SELECTION_CHANGE_PRESSED;
                    break;
                }

                if (presses & PIN6_bm) {
                    // S3 makes selection
                    music_init(file_idx);
                    display_dp_sides(1, 1);
                    state = SELECTION_MADE_PRESSED;
                }

                break;
            }
            case SELECTION_CHANGE_PRESSED: {
                uint8_t releases = get_releases();

                // Only check for S1 and S2 to be released
                if (releases & (PIN4_bm | PIN5_bm)) {
                    state = SELECTION_IDLE;
                }

                break;
            }
            case SELECTION_MADE_PRESSED: {
                uint8_t releases = get_releases();

                // Only wait for S3 to be released
                if (releases & PIN6_bm) {
                    state = SELECTION_AWAITING_CONFIRMATION;
                }

                break;
            }
            case SELECTION_AWAITING_CONFIRMATION: {
                uint8_t presses = get_presses();

                // S1, S2, S3 cancels selection
                if (presses & (PIN4_bm | PIN5_bm | PIN6_bm)) {
                    music_stop();
                    state = SELECTION_CANCEL;
                    break;
                }

                // S4 plays music
                if (presses & PIN7_bm) {
                    music_play();
                    state = MUSIC_PLAYING;
                }

                break;
            }
            case SELECTION_CANCEL: {
                uint8_t releases = get_releases();

                // Only wait for S1, S2, S3 to be released
                if (releases & (PIN4_bm | PIN5_bm | PIN6_bm)) {
                    display_dp_sides(0, 0);
                    state = SELECTION_IDLE;
                }

                break;
            }
            case MUSIC_PLAYING: {
                uint8_t presses = get_presses();

                // S3 pauses music
                if (presses & PIN6_bm) {
                    music_pause();
                    state = MUSIC_PAUSED_IDLE;
                    break;
                }

                // Parse next music code if needed
                if (is_playing && read_next_code) {
                    char word[10];
                    uint8_t word_len = read_word(&sheet_reader, word, sizeof(word));

                    if (!word_len) {
                        should_stop = 1;
                        break;
                    }

                    parse_music_code(word);
                } else if (!is_playing && should_stop) {
                    // Music has finished
                    display_num(file_idx + 1);
                    display_dp_sides(0, 0);
                    state = SELECTION_IDLE;
                }

                break;
            }
            case MUSIC_PAUSED_IDLE: {
                uint8_t presses = get_presses();

                // S2 stops music
                if (presses & PIN5_bm) {
                    music_stop();
                    display_num(file_idx + 1);
                    display_dp_sides(0, 0);
                    state = MUSIC_STOPPING_PRESSED;
                    break;
                }

                // S4 continues playing music
                if (presses & PIN7_bm) {
                    music_play();
                    state = MUSIC_PLAYING;
                }

                break;
            }
            case MUSIC_STOPPING_PRESSED: {
                uint8_t releases = get_releases();

                // Only wait for S2 to be released
                if (releases & PIN5_bm) {
                    state = SELECTION_IDLE;
                }

                break;
            }
            default: {
                file_idx = 0;
                display_num(1);
                display_dp_sides(0, 0);
                break;
            }
        }
    }
}