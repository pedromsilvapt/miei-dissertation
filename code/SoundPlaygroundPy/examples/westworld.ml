fun mainTheme () {
    S6/8 T70 L/8 V120;

    :violin = 41;

    $chorus = (A*11 G F*12 | A,6 A,5 G, F,6*2);

    $melody = (r24   (:violin a3 c'3 d'3 e'9) r9 e'3 d'3 c'3 a9);

    play( $chorus*3 | $melody );
};

play( mainTheme() );
