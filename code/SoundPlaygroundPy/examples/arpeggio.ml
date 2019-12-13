# $accord = voices\create( "accord"; 22; S3/4 T120 L/4 );

S3/4 T120 L/4;

cc( 64; 0 );

setinstrument( 22 );

$e1 = ( c5/2 r/2 | r [cde][cde] );
$e2 = ( c5/2 r/2 );
$pat = $e1;

keyboard repeat toggle {
    a: arpeggio( Cm; $pat );
    s: arpeggio( Fm; $pat );
    d: arpeggio( Gm; $pat );

    8: setvar( $pat; $e1 );
    9: setvar( $pat; $e2 );
}
