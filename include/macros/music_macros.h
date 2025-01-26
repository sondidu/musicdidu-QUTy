#ifndef MUSIC_MACROS_H
#define MUSIC_MACROS_H

#define FREQ_CLK_DIV2 1666667
#define PPQN 24

// Formula: 20/6 * 10^6 / 2 / desired_freq
// Note frequencies: https://mixbutton.com/mixing-articles/music-note-to-frequency-chart/

#define NOTE_PER_C 6370 // 6370.319408, 261.63 Hz
#define NOTE_PER_D 5675 // 5674.497741, 293.66 Hz
#define NOTE_PER_E 5056 // 5056.174094, 329.63 Hz
#define NOTE_PER_F 4772 // 4772.404051, 349.23 Hz
#define NOTE_PER_G 4252 // 4251.700680, 392 Hz
#define NOTE_PER_A 3788 // 3787.878787, 440 Hz
#define NOTE_PER_B 3375 // 3374.638914, 493.88 Hz

#define NOTE_PER_C_SHARP 6013 // 6012.939847, 277.18 Hz
#define NOTE_PER_D_SHARP 5357 // 5356.817622, 311.13 Hz
#define NOTE_PER_E_SHARP NOTE_PER_F
#define NOTE_PER_F_SHARP 4505 // 4504.626251, 369.99 Hz
#define NOTE_PER_G_SHARP 4013 // 4013.163175, 415.30 Hz
#define NOTE_PER_A_SHARP 3575 // 3575.310337, 466.16 Hz
#define NOTE_PER_B_SHARP 3185 // 3185.220577, 523.25 Hz

#define NOTE_PER_C_FLAT 6749 // 6749.277827, 246.94 Hz
#define NOTE_PER_D_FLAT NOTE_PER_C_SHARP
#define NOTE_PER_E_FLAT NOTE_PER_D_SHARP
#define NOTE_PER_F_FLAT NOTE_PER_E
#define NOTE_PER_G_FLAT NOTE_PER_F_SHARP
#define NOTE_PER_A_FLAT NOTE_PER_G_SHARP
#define NOTE_PER_B_FLAT NOTE_PER_A_SHARP

#define OCTAVE_STANDARD 4

#define PREFIX_ANACRUSIS 'a'
#define PREFIX_BPM 'b'
#define PREFIX_FERMATA 'f'
#define PREFIX_TIME_SIGNATURE 't'

#endif
