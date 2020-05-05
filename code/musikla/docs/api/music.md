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

### scale ( intervals : List[int] )
Creates a scale with the given intervals. There are two predefined scales, `$scales::white_keys` and `$scales::black_keys`. The scales wrap around, going up octaves or down, when the index is negative.

    #!musikla
    play( C + $scale::white_keys::[ 1 ] ) # will play D

    play( C + $scale::white_keys::[ 8 ] ) # will play d