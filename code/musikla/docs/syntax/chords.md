# Chords
We've already covered how we can play multiple notes at the same time thanks to the [parallel operator](combinators.md#parallel).
However, there is a handy shortcut to produce chords, that also has the benefit of identifying semantically that those notes are indeed part of the same chord.

    #!musikla
    [CFG]/2 [CFG]
    # Is roughly equivalent to
    (C/2|F/2|G/2) (C|F|G)

As can be seen, wrapping the notes in square brackets `[` `]` avoids the need to manually put all notes in parallel. It also avoids the need to set the [length](notes-and-rests.md#note-lengths) of each note manually.

However, instead of typing each individual note of the chord, it is also possible to create a chord from a *root note* and specifying the type of chord needed.

    #!musikla
    [Cm]/2 [CM]

## Chord Abbreviations
As of now, the supported chord abbreviations are as follows:

|     Group     | Abbreviations                                         |
|---------------|-------------------------------------------------------|
| Triads        | `M` / `m` / `aug` / `dim` / `+`                       |
| Sevenths      | `m7` / `M7` / `dom7` / `7` / `m7b5` / `dim7` / `mM7`  |
| Perfect Fifth | `5`                                                   |