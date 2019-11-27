fun mainTheme () {
    # :piano = (1; S6/8 T70 L/8 V120 );
    # :violin = :piano(41);
    $piano = voices\create( "piano"; 1; S6/8 T70 L/8 V120 );
    $violin = voices\create( "violin"; 41; V120; $piano );

    $chorus = :piano (A*11 G F*12 | A,6 A,5 G, F,6*2)*3;

    $melody = :piano (r24   (:violin a3 c'3 d'3 e'9) r9 e'3 d'3 c'3 a9);

    play( :piano $chorus | :piano $melody );
};

play( mainTheme() );
