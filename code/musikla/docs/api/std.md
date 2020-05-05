# std

This module contains the most common and basic functions. Those functions are always available and don't require a custom import.

## Functions
### print( \*args )
The standard *Python* print function.

### debug( value )
Similar to `print`, but handles musical sequences differently (iterating over them and printing the notes/music events inside them).

### discard( value )
Simply consumes the value but does not return it. Useful when the value is a musical expression, since musical expressions that are used as statements are implicitly played.

    #!musikla
    C F G;
    # Is implicitly equivalent to
    play( C F G );

    # If we did not want to play them we could use
    discard( C F G );

While using this function with literal musical values might seem pointless, it can be useful when calling custom functions that might return music but also have some sort of side effects. With discard, we can execute those side effects without playing the music.

    #!musikla
    fun custom_function ( ref $count ) {
        $count += 1;

        play( C F G );
    };
    
    $i = 0;

    # No music will be played here
    discard( custom_function( $i ) );

    # But the value of $i is changed to 1
    print( $i );

### using( variable )
When running code inside a function, any variable assignment is assumed to refer to a local variables (similar to the behavior of functions in Python). However, if we wanted to use a global variable inside our function, we need to specifically state we are *using* it.

    #!musikla
    $global = 0;
    fun without_using () { 
        $global = 1; 
    };

    fun with_using () { 
        using( $global );

        $global = 1; 
    };

    without_using();
    print( $global ); # prints 0, global isn't changed
    with_using();
    print( $global ); # prints 1, global is changed

### mod ( n : float, d : float )
Calculates the modulo. Similar to the `%` python operator.

    #!musikla
    # Equivalent to `5 % 2` in python
    mod( 5, 2 );

### div ( n : float, d : float )
Calculates the integer division. Similar to the `//` python operator.

    #!musikla
    # Equivalent to `5 // 2` in python
    div( 5, 2 );

### ord ( char : str )
Returns an integer corresponding to the character provided.

    #!musikla
    print( ord( 'A' ) );    # 65

### chr ( n : integer )
Returns the character corresponding to the integer provided.

    #!musikla
    print( chr( 65 ) );    # 'A'

### gettime ()
Return the current timestamp in milliseconds

### settime ( time : int )
Set the current timestamp to `time`, in milliseconds. Use with care so as to not break the principle or ordered events.