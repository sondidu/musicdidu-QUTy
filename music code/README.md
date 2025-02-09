# Music Code Directory

**Music code** is code that represents notes, rests, and other important musical information that will be parsed during runtime. This directory is only for viewing purposes and the actual contents of music code is stored in the [QUTy](https://cab202.github.io/quty/)'s flash through the generated `data.c` file in the [src/](../src) directory.

The purpose of having music code is to make parsing during runtime easy and efficient. There are six types of music codes:

- `b{BPM period value}`: `b` followed by the BPM's period value that is calculated during validation.
- `a{anacrusis ticks}`: `a` followed by the number of ticks of the anacrusis bar.
- `t{beats per bar}/{beat value}`: `t` followed by two numbers separated with a `/` representing the beats per bar and beat value respectively.
- `*{rest ticks}`: `*` followed by the number of ticks it is resting.
- `[{f}]{play ticks}{note char}{octave}{rest ticks}`: A structure that represents what note, at what octave, how long it should play and how long it should rest afterwards. It can optionally begin with a `f` to indicate that the note is a fermata. It's also important to note that `{note char}` is a single character that represents the note symbol and also whether it has a sharp or flat. Check the source code to understand why it's possible to use a single character. 😏