# Notes & Rests
In Musikla, notes are first-class primitives, just like numbers or strings or booleans are in most programming languages. This means we can put notes anywhere a value is expected, without the need for any special syntax. Also of note, any notes that are not stored in a variable or passed to a function are played automatically. Calling the `play()` function is optional.

## Notes
Notes are represented by the letters `C`, `D`, `E`, `F`, `G`, `A` and `B`. Middle *C*, also known as *C4*, is represented by `C`.

### Octaves
To lower the octave, we can add commas `,` after the note. To up one octave, we can first use the lower case letter `c`, and to up further we can add apostrophes `'` after the letter.

Here is a full scale of C's:
```musikla
C,,,, C,,, C,, C, C c c' c'' c''' c'''' c'''''
```

The lowest possible note is `C,,,,` and the highest is `g'''''`.

### Accidentals
It is possible to describe accidentals by prefixing the note with either `^^`, `^`, `_` or `__`. Thus, it is possible to represent all the keys in a piano like so:
```musikla
C ^C D ^D E ^F F ^G G ^A A B
```

> **Note** In practice `^^C == D` and `__D == C`;

### Note Lengths
Not all notes have the same length (or duration). The default length of all notes is 1 beat. This can be changed by appending the note with its length.

  - `C1/2` (or the equivalent `C/2`) describes a **half note** (or a *minim*)
  - `C1` (or the equivalent `C`) describes a **whole note** (or a *semibreve*)
  - `C2` describes a **double whole note** (or a *breve*)

The actual duration of the note (in seconds) is determined by the beats per minute (*BPM*) and the time signature of the current [voice](voices.md).

## Rests
Rests allow us to describe pauses: moments of silence between notes. They are described by the letter `r`. The length of a rest can be described in the same way as the  [length of a note](#note-lengths).
```musikla
c2 r3/4 c
```
