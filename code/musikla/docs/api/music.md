# music

Functions specificly related to the `Music` data type are contained in this module.

 > **NOTE** This module is automatically imported for all scripts, and thus never needs to be manually imported.

## Functions
### cc( control : int, value : int )
Emits a `ControlChangeEvent` for the current voice. The controls available and their valid values are the taken from the *MIDI* specification are listed [here](https://www.midi.org/specifications-old/item/table-3-control-change-messages-data-bytes-2).

    #!musikla
    # Sustain On
    cc( 64, 127 );
    # Sustain Off
    cc( 64, 0 );

### setvoice( voice : Voice )
Changes the current voice to the voice given. Note that the voice should be passed as a variable (with a `$` prefix) instead of the usual `:` voice prefix.

    #!musikla
    :violin = 41;

    setvoice( $violin );

### setinstrument( instrument : int )
Keeps the same voice but changes it's instrument. Expects a number representing the intrument ID (usually follows the [General MIDI](https://en.wikipedia.org/wiki/General_MIDI) specification).

    #!musikla
    setinstrument( 41 );

### sfload( soundfont : str, alias : str = none, only_new : bool = false )
Loads a custom soundfont. An optional alias can be passed in to avoid having to reference the full file path everytime we want to set instruments.

    #!musikla
    sfload("/path/to/Blanchet-1720.sf","bl")

    setinstrument( 4, 1, "bl" );

### sfunload( soundfont : str, only_new : bool = false )
Unloads and releases the resources associated with a soundfont. Can pass either the file path or the alias (if the font has one).

    #!musikla
    sfunload( "bl" );

### interval( semitones : int = 0, octaves : int = 0 )
Creates an interval with the given semitones and octaves. Both parameters are optional, and can be used as positional or named parameters.

    #!musikla
    # An interval with three semitones
    $int = interval( 3 );
    # An interval with two octaves
    $int = interval( octaves = 2 );
    # An interval with two octaves and three semitones
    $int = interval( 3, 2 );

Intervals can be added and subtracted with each other, as well as with plain integers (treated as semitones).

    #!musikla
    # An interval with three semitones
    $int = interval( 3 );

    print( ( $int + 1 )::semitones ) # prints out 4

They can also be added to Music sequences or single note events, effectively transposing the notes with the given interval.

    #!musikla
    # Adds two semitones
    play( ( C F G ) + 2 );

    # Adds two octaves
    play( ( C F G ) + interval( octaves = 2 ) );

### scale( intervals : List[int] )
Creates a scale with the given intervals. There are two predefined scales, `$scales::white_keys` and `$scales::black_keys`. The scales wrap around, going up octaves or down, when the index is negative.

    #!musikla
    play( C + $scale::white_keys::[ 1 ] ) # will play D

    play( C + $scale::white_keys::[ 8 ] ) # will play d

### save( music, outputs )
Save a music expression to a sequencer. The sequencers can either be:

 - A `str`, such as a file name.
 - A `Sequencer` instance, created with [make\_sequencer](#make-sequencer) for example.
 - A of sequencers' options

<span></span>

    #!musikla
    $melody = A, E A B;

    # We can save directly to files, the format is guessed based upon
    # the file extension
    save( $melody, "file.wav" );

    # We can also pass custom options, and even save to multiple sequencers
    save( $melody, @[
        # First output, a WAV file with custom options
        @[ "-o", "file.wav", "-g", "1" ],
        # Second output, a MIDI file with default options
        "file.midi"
        # Could have more outputs if needed
    ] );