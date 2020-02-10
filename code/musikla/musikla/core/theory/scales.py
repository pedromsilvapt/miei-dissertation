from typing import List

# major: W W H W W W H
# minor: W H W W H W W
def build_scale ( steps : List[int] ) -> List[int]:
    notes = [ 0 ]

    acc = 0

    for s in steps:
        acc += s

        notes.append( acc )

    return notes

def inverted ( intervals : List[int], count : int ) -> List[int]:
    if count > 0:
        for i in range( 0, count ):
            intervals[ i ] += 12
    else:
        for i in range( 0, count * -1 ):
            intervals[ i ] -= 12

    return intervals

major_intervals = [ 2, 2, 1, 2, 2, 2, 1 ]

major = build_scale( major_intervals )

minor_intervals = [ 2, 1, 2, 2, 1, 2, 2 ]

minor = build_scale( minor_intervals )

major_chord = build_scale( [ 4, 3 ] )

minor_chord = build_scale( [ 3, 4 ] )
