# :left = ( 1; S4/4 T74 L/8 V90 ); 
$left = voices\create( "left"; 1; S4/4 T74 L/8 V90 );
# :right = :left( 1; V90 ); 
$right = voices\create( "right"; 1; V90; $left );

$wet\acomp = (:left     A, E A B ^c B A E D ^F ^c e ^c A3);
$wet\melody = (:right   ^g6 a2 ^f6);

fun wet () {
    $wet\acomp * 2 | :right r8*2 $wet\melody;
};

wet();
