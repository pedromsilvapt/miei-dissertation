$accord = voices\create( "accord"; 22; S3/4 T120 L/4 );

cc( 64; 0 );

$pt = [cde][c'd'e']cdecdeedc;
$e1 = :accord ( c5/2 r/2| r [cde][cde]);

# play( $e1 );

keyboard repeat hold {
    a: arpeggio( Cm; $e1 );
    s: arpeggio( Fm; $e1 );
    d: arpeggio( Gm; $e1 );
}
