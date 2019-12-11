# $accord = voices\create( "accord"; 22; S3/4 T120 L/4 );
setinstrument( 22 );
S3/4 T120 L/4;

cc( 64; 0 );

$e1 = ( c5/2 r/2 | r [cde][cde] );

keyboard repeat toggle {
    a: arpeggio( Cm; $e1 );
    s: arpeggio( Fm; $e1 );
    d: arpeggio( Gm; $e1 );
}
