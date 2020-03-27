from typing import List
from .interval import Interval

class Scale:
    def __init__ ( self, intervals : List[int] ):
        self.intervals : List[int] = intervals

    def interval_at ( self, index : int ) -> Interval:
        l = len( self.intervals )
        
        return Interval( octaves = index // l, semitones = self.intervals[ index % l ] )

Scale.black_keys = Scale( [ 1, 3, 6, 8, 10 ] )

Scale.white_keys = Scale( [ 0, 2, 4, 5, 7, 9, 11 ] )

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

# Triads
major_triad = build_scale( [ 4, 3 ] )

augmented_triad = build_scale( [ 4, 4 ] )

minor_triad = build_scale( [ 3, 4 ] )

diminished_triad = build_scale( [ 3, 3 ] )

# Sevenths
minor_seventh = build_scale( [ 3, 4, 3 ] )

major_seventh = build_scale( [ 4, 3, 4 ] )

dominant_seventh = build_scale( [ 4, 3, 3 ] )

diminished_seventh = build_scale( [ 3, 3, 3 ] )

half_diminished_seventh = build_scale( [ 3, 3, 4 ] )

minor_major_seventh = build_scale( [ 3, 4, 4 ] )

# Perfect Fifth
perfect_fifth = build_scale( [ 7 ] )

chords = {
    'm': minor_triad,
    'M': major_triad,
    'dim': diminished_triad,
    'aug': augmented_triad,
    '+': augmented_triad,

    'm7': minor_seventh,
    'M7': major_seventh,
    'dom7': dominant_seventh,
    '7': dominant_seventh,
    'm7b5': half_diminished_seventh,
    'dim7': diminished_seventh,
    'mM7': minor_major_seventh,

    '5': perfect_fifth
}