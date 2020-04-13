# Voices
Voices allow a easy way of grouping notes and applying settings to all of them, such as the volume or instrument. By default, there is already one voice created and all notes played are played in that voice.

## Modifiers
To change the settings of a voice, we make use of **modifiers**. Modifiers can be used anywhere notes can, and can be even used in the middle of notes.

    #!musikla
    S4/4 L1/4 V90

One interesting aspect is that by using [groups](combinators.md#grouping), we can apply those modifiers to just a subset of notes. In the example below, we can see how to apply a change in volume `v50` to only the notes that are inside the parenthesis.

    #!musikla
    C ( v50 F ) G

| Modifier              | Description                                                                                                                               |
|:---------------------:|-------------------------------------------------------------------------------------------------------------------------------------------|
| **S4/4**              | Changes the time signature to **4/4**.                                                                                                    |
| **L2** <br/> **L1/2** | Sets the base [note length](notes-and-rests.md#note-lengths). Each note's length is then calculated as a multiplier of this value.        |
| **T120**              | Changes the tempo to **120** beats per minute (*BPM*).                                                                                    |
| **O1**                | Sets the base octave to **1**. `C` becomes `C1` (instead of `C4`) and all other notes change as well                                      |
| **I1**               | Change the voice's instrument to be the number **1** (usually follows the [General MIDI Standard](https://en.wikipedia.org/wiki/General_MIDI) |

## Named Voices
Sometimes instead of changing the settings of the voice in everyplace we need them, we might want to create named voices. These voices can have default settings that 
are automatically applied when we change to that voice.

Voice names are prepended by a colon `:`. The simplest voice declaration is to just define the name and instrument to be used. Using the name we just created, we can then change the voice anywhere.

    #!musikla
    :violin = I41;

    C F G ( :violin c f g );

However, voices can also be used to change more than just the instrument. We can pass them a sequence of modifiers as well, and they will be applied by default to the voice. Optionally, we can inherit those settings from other voices, to avoid typing them out one by one.

    #!musikla
    :piano = I1 S6/8 T140 L/8 V120;
    :violin = :piano( I41 );
