# Programming
A **musikla** script is just a sequence of statements ( and expressions ). Each statement must be followed by a `;`, even if it ends in brackes `{` and `}` like an `if` or `while`.

## Variables
Variables can stored and accessed by prefixing their name with a dollar sign `$.

    #!musikla
    $var_name = true;

    print( $var_name == null or $var_name == false );


## Function Declarations
Functions are declared with the `fun` keyword, followed by an optional function name. Function declarations are expressions that return a reference to the newly created function. This means that they can be saved in variables, passed as parameters to other functions, or otherwise used anywhere an expression could generally be used.

    #!musikla
    fun hello_world ( $name = 'User' ) {
        return 'Hello ' + $name;
    };


Function bodies can be multiline (like in the example above, surrounded by brackets `{`  `}`) or single line indicated by an arrow `=>`

    #!musikla
    fun hello_world ( $name = 'User' ) => 'Hello ' + $name;


### Reference Arguments
Function arguments can be declared as `ref`, meaning that any changes done to them will be reflected on the variable outside the function. Reference 

    #!musikla
    fun increment ( ref $var ) {
        $var += 1;
    };

    $a = 0;

    inc( $a );

    print( $a ); # prints 1

## If/Else
Right now `else if`'s are not supported. The `else` block is optional, of course.

    #!musikla
    if ( $condition ) {
        print( 1 );
    } else {
        print( 2 );
    };

## While

    #!musikla
    while ( $condition ) {
        print( 1 );
    };

## For

    #!musikla
    for ( $item in $collection ) {
        print( $item );
    };

## Arrays
Arrays are a very common construct in programming languages, and they have proven very useful here as well.

Array literals can be constructed with the syntax `@[]`

    #!musikla
    $array = @[ 1, 2, 3, 4 ];

    # Iterate over the array
    for ( $i in $array ) {
        print( $i );
    };

    # Print the first and last element of the array
    print( $array::[ 0 ], $array::[ -1 ] );

## Dictionaries
Similar to arrays, dictionary literals can be constructed with the syntax `@{}`

    #!musikla
    $dict = @{ foo = 1, bar = true, get = 1 };

Dictionaries have four methods: `has()`, `get()`, `set()` and `delete()`. For convenience, their values can also be accessed using the regular property accessor syntax.

    #!musikla
    # We check if the key exists, and access it directly
    if ( $dict::has( 'foo' ) ) {
        print( $dict::foo );
    };
    
    # With the `get` method we can provide a default value
    print( $dict::get( 'foo', default = null ) );

    $dict::set( 'bar', false );

    $dict::delete( 'foo' );
