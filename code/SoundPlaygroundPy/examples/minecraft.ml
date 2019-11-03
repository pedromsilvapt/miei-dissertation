$wet\acomp = (S4/4 T74 L/8   V90 A, E A B ^c B A E D ^F ^c e ^c A3);
$wet\melody = (S4/4 T74 L/8  ^g6 a2 ^f6);

fun wet () {
    $wet\acomp * 2 | S4/4 T74 L/8 r8*2 $wet\melody;
};

wet();
