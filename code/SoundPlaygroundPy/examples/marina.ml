# Title: Soft to Be Strong
# Artist: Marina

V70 L1 T120;

fun accomp () {
    ^Cm;
    BM; 
    AM; 
    BM
    ^Cm;
    AM; 
    BM2;

    ^Cm;
    BM;
    AM;
    BM;
    ^Cm;
    AM;
    BM2;
};

fun melody () {
    V120;

    r/4 ^g/4 ^g/4 ^g/4;
    ^f/2 e/8 ^d3/8; 
    ^c2;

    r/4 ^g/4 b/4; 
    ^c'/2 ^c'/4 ^c'/4;
    b5/4; 
    b/8 e'/8 ^d'/8 e'/8 b/4;
    ^c'/4 ^g/4 ^g/4 ^g/4;
    ^f/2 e/8 ^d3/8;
    ^c2;

    r/4 ^g/4 b/4;
    ^c'/2 ^c'/4 ^c'/4;
};

fun toggle_sustain ( ref $enabled ) {
    if $enabled {
        cc( 64; 0 );
    } else {
        cc( 64; 127 );
    };

    $enabled = not $enabled;
};

fun keyboard () {
    $sustained = true;

    keyboard { q toggle: accomp() | melody(); };
    
    keyboard hold extend {
        a: ^Cm;
        s: BM;
        d: AM;
        f: EM;
        g: ^Fm;
    };
    
    keyboard hold extend (V120) {
        1: ^c;
        2: ^d; 
        3: e;
        4: ^f;
        5: ^g;
        6: b;
        7: ^c';
        8: ^d';
        9: e';

        c: toggle_sustain( $sustained );
    };
};

keyboard();
