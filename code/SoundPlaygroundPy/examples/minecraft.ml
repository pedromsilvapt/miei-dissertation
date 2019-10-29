fun wet () {
    S4/4 T74 L/8;

    $acomp = (V90 A, E A B ^c B A E D ^F ^c e ^c A3);

    $melody = (r8*2  ^g6 a2 ^f6);

    play( $acomp * 2 | $melody );
};

play( wet() );
