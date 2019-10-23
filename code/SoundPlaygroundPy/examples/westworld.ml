S6/8 T70 L/8 V120;

:violin = 41;

fun music( $chorus; $melody ) {
    play( $chorus*3 | $melody );
};

$chorus = (A/8*11 G/8 F/8*12 | A,6/8 A,5/8 G,/8 F,6/8*2);

$melody = (r3 L3/8 (:violin a c' d' e'9/8) r9/8 e' d' c' a9/8);

play( music( $chorus; $melody ) );

register_key( "ctrl+a"; A );
register_key( "ctrl+b"; B );
