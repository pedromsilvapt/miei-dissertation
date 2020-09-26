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

### getctx()
Returns the current context object.

    #!musikla
    print( getctx()::voice::tempo ); # 60
    print( getctx()::voice::time_signature ); # (4, 4)

### withctx(ctx, expr)
Evaluates the expression on the second argument with the context provided in the first argument.

    #!musikla
    fun some_function () {
        # All musikla functions have a special variable '$__callerctx__'
        # that contains a reference to the context of the caller
        # With it we can modify it's context (i.e. changing variables)
        withctx( $__callerctx__, {
            $i = 1;
        } );
    };

    $i = 0;

    some_function();

    print( $i ); # 1
    

### ast ( expr : any )
Instead of evaluating the expression that is passed to it, simply returns the AST Node object of the argument.

    #!musikla
    $node = ast( ^C4 );
    
    print( $node::__class__::__name__ ); # NoteNode
    print( $node::note::pitch_class ); # 0
    print( $node::note::value ); # 4
    print( $node::note::accidental ); # 1


### ast_to_code ( node : Node, ident : int = 4 )
Converts an AST node to a string representing the source code. Useful for debugging.

### parse ( code : str )
Similar to the [ast](#ast) function, but takes a string instead of an expression. Is useful to create code dynamically at runtime.

    #!musikla
    $node = parse( '^C4' );
    
    print( $node::__class__::__name__ ); # NoteNode
    print( $node::note::pitch_class ); # 0
    print( $node::note::value ); # 4
    print( $node::note::accidental ); # 1

### eval ( code : str | Node )
Evaluates a snippet of Musikla code with the current context. If a string is provided, parses it first.

    #!musikla
    print( eval( '3 * 2' ) ); # 6

    # Evals can have side-effects too
    eval( '$var_name = 25' );

    print( $var_name ); # 25

### pyeval ( code : str )
Allows executing arbitrary strings of Python code. Follows the same rules as [embedding python expressions](../getting-started/programming.md#embedding-python), which means Musikla variables can be read from.

    #!musikla
    $arr = @[ 1, 2, 3 ];

    # We can use Python's list comprehensions to manipulate our array
    $arr = pyeval( '[ i * 2 for i in arr ]' );

### pyexec ( code : str )
Allows executing arbitrary strings of Python code. Follows the same rules as [embedding python blocks](../getting-started/programming.md#embedding-python), which means Musikla variables can be read/written to. Also allows exporting functions or other variables from the Python code.

    #!musikla
    pyexec(
        'import os\n' +
        'export( "os" )( os )\n'
    );

    # Since we exported the 'os' module, we can access it in the current scope
    print( $os::name );

### pymodule ( module : str, variables : str | List[str] = none )
Loads a python module. If variables is a string, returns only that symbol. If it is a list, returns a tuple with the symbols.

    #!musikla
    # Import the entire os module
    $os = pymodule( 'os' );

    # Import only a single class
    $Path = pymodule( 'pathlib', 'Path' );

    # Import multiple functions
    $basename, $dirname = pymodule( 'os.path', @[ 'basename', 'dirname' ] );

### getcwd()
Returns the current working directory
