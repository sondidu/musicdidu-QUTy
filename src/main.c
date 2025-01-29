#include <avr/io.h>
#include <avr/interrupt.h>

#include "buttons.h"
#include "buzzer.h"
#include "display.h"
#include "flash.h"
#include "music.h"
#include "timers.h"
#include "uart.h"

void inits(void) {
    cli();
    buttons_init();
    buzzer_init();
    tcb1_init();
    display_init();
    uart_init();
    music_init(1);
    sei();
}

int main(void) {
    inits();

    music_play();

    while(1) {
        if (is_playing && read_next_code) {
            char word[10];
            uint8_t word_len = read_word(&sheet_reader, word, sizeof(word));

            if (!word_len) {
                should_stop = 1;
                continue;
            }

            parse_music_code(word);
        }
    }
}