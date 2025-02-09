# Sheets Directory

This directory contains music sheet files in `.txt` format. Each file represents a different piece of music that can be played by the [QUTy](https://cab202.github.io/quty/) board.

## Validation Rules and Creating Your Own Sheets
Each sheet is a `.txt` file that must follow a set of rules to build successfully. Each sheet must contain **blocks**, which can be either a **setting block** or a **bar** (in this context, 'bar' refers to actual bars in music theory). Music knowledge isn't mandatory but will definitely help 😄.

### Setting Block
A **setting block** follows JSON's syntax closely. It is text enclosed with curly brackets `{}` with **setting fields** separated by a commas `,`, but must all be in a single line. **Setting fields** are case-sensitive and are key-value pairs separated by an equal sign `=`. These are the valid key-value pairs of a **setting field**:
- `BPM`: Beats Per Minute is two positive integers separated by a `/`. The first number is the desired BPM value, and the second number is the beat value. Valid beat values are: 1, 2, 4, 8, 16, and 32. The beat value can optionally have a `.` to indicate that beat value is a dotted note. Not all possible combinations of BPM and beat values are possible, learn why [here](#some-bpm-and-beat-value-combinations-arent-possible).
- `tsig`: Time signature is two positive integers separated by a `/`. The first number is the **number of beats per bar** (a.k.a beats per measure), and the second number is the **beat value**. Valid values for beat value are: 1, 2, 4, 8, 16, and 32.
- `anacrusis`: Anacrusis represents whether the next bar should have its beats validated. By default, all **bars** must have the right number of beats based on the current time signature. To declare the next **bar** an anacrusis bar, set the value to `True`.
- `skipbars`: The number of bars to skip processing.

Here's an example of a **setting block**:
`{ BPM=100, tsig=4/4, anacrusis=True }`

#### Why Some BPM and Beat Value Combinations aren't Possible
Some BPM and beat value combinations aren't posssible because of the hardware limitation of the QUTy's TCB. The QUTy uses an [ATTINY1626](https://ww1.microchip.com/downloads/en/DeviceDoc/ATtiny1624-26-27-DataSheet-DS40002234A.pdf) microcontroller which has a 16-bit timer TCB. Therefore, small BPM values are limited to the TCB's maximum Capture Compare (CCMP) value which is 65535. Examples of the smallest possible values are `64/4` and `128/8` that is 64 BPM with beats as quarter notes and 128 BPM with beats as eighth notes. Any equivalent BPM lower would result in an error.

### Bar
Bars represent actual bars in music theory. A bar contains **musical elements** separated by spaces, enclosed in square brackets `[]`, and must all be in a single line. Covering every possible musical element is challenging, so I have decided to limit the scope to three elements: notes, rests, and tuplets. Each bar can have any number of elements as long as it follows each element's rules and the beats add up to the current time signature.

#### Note
A note follows the structure `{note}-{duration}-{additionals}`.
- `note` can be `A`, `B`, `C`, `D`, `E`, `F`, or `G`, optionally followed by `#` or `b` (to represent sharp or flat, respectively), and an octave number. The octave number must be an integer from 1 to 8.
- `duration` is either 1, 2, 4, 8, 16, or 32, representing the fraction of the note. That means 1 is a whole note, 2 is a half note, 4 is a quarter note, and so on.
- `additionals` is one or more characters representing additional attributes for the note. The possible characters and what they represent:
  - `.`: dotted note
  - `@`: fermata (in this project, the note is played twice its original duration without affecting beat calculation)
  - `<`: beginning of a slur
  - `>`: end of a slur
  - `s`: staccato

Note examples:
- `A4-4`: A quarter note playing `A` on the 4th octave
- `C#5-8`: An eighth note playing `C#` on the 5th octave
- `D6-4-.`: A dotted quarter note playing `D` on the 6th octave

#### Rest
A rest follows the structure `*-{duration}`.
Just like durations for [notes](#note), it represents the fraction of the rest, with possible values being 1, 2, 4, 8, 16, and 32.

Rest examples:
- `*-1`: Whole rest
- `*-2`: Half rest
- `*-4`: Quarter rest

#### Tuplet
A tuplet follows the structure `{grouping}:{number of regular notes}:{duration of regular note}({element1}_{element2}_{element3}_...)`.
- `grouping` is an integer representing the typical number of notes for the tuplet. For example, a 3 represents a triplet, a 5 represents a quintuplet, etc.
- `number of regular notes` is an integer representing the actual number of regular notes.
- `duration of regular note` is an integer representing the duration (in fractions) of regular notes.

In this project, all elements within the brackets `()` are separated by underscores `_`. The beats of all the elements must add up to `grouping * duration of regular note`. However, the actual beats is `number of regular notes * duration of regular note`. Elements can only be [notes](#note) or [rests](#rest), but not tuplets themselves.

Tuplet examples:
- `3:2:4(C4-4_D4-4_E4-4)`: Three quarter notes playing `C4`, `D4`, and `E4` in the span of two quarter notes
- `5:4:4(F4-4_G4-4_A4-4_B4-4_C5-4)`: Five quarter notes playing `F4`, `G4`, `A4`, `B4`, and `C5` in the span of four quarter notes
- `3:2:8(C4-16_D4-16_E4-16_F4-16_G4-8)`: Four sixteenth notes `C4`, `D4`, `E4`, and `F4` and an eighth note `G4` in the span of three eighth notes.

Additionally, you can optionally create a file `whitelist` (without extensions) and on each line, give the name of the files (excluding `.txt`) that you want to be processed. If the file isn't present, then all the `.txt` files in this directory are processed.
