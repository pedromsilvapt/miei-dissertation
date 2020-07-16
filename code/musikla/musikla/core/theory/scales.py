from typing import Any, Callable, List, Optional
from .interval import Interval

ScaleMapper = Callable[[Interval, int, 'Scale'], Any]

class Scale:
    black_keys : 'Scale'
    black_keys_padded : 'Scale'
    white_keys : 'Scale'
    pentatonic_major : 'Scale'

    # major: W W H W W W H
    # minor: W H W W H W W
    @classmethod
    def steps ( cls, steps ):
        notes = [ 0 ]

        acc = 0

        for s in steps:
            acc += s

            notes.append( acc )

        return cls( notes )

    def __init__ ( self, intervals : List[int], mapper : ScaleMapper = None ):
        self.intervals : List[int] = intervals
        self.mapper : Optional[ScaleMapper] = mapper

    def __len__ ( self ):
        return len( self.intervals )

    def __getitem__ ( self, key ) -> Interval:
        return self.interval_at( key )

    def __iter__ ( self ):
        for i in range( len( self ) ):
            yield self[ i ]

    def map ( self, mapper : ScaleMapper ) -> 'Scale':
        return Scale( self.intervals, mapper )

    def interval_at ( self, index : int ) -> Interval:
        l = len( self.intervals )
        
        interval = Interval( octaves = index // l, semitones = self.intervals[ index % l ] )

        if self.mapper is not None:
            return self.mapper( interval, index, self )
        
        return interval

Scale.black_keys = Scale( [ 1, 3, 6, 8, 10 ] )

Scale.black_keys_padded = Scale( [ 1, 3, 3, 6, 8, 10, 10 ] )

Scale.white_keys = Scale( [ 0, 2, 4, 5, 7, 9, 11 ] )

Scale.pentatonic_major = Scale( [ 0, 2, 4, 7, 9 ] )

def inverted ( intervals : List[int], count : int ) -> List[int]:
    if count > 0:
        for i in range( 0, count ):
            intervals[ i ] += 12
    else:
        for i in range( 0, count * -1 ):
            intervals[ i ] -= 12

    return intervals

major_intervals = [ 2, 2, 1, 2, 2, 2, 1 ]

major = Scale.steps( major_intervals )

minor_intervals = [ 2, 1, 2, 2, 1, 2, 2 ]

minor = Scale.steps( minor_intervals )

# Triads
major_triad = Scale.steps( [ 4, 3 ] )

augmented_triad = Scale.steps( [ 4, 4 ] )

minor_triad = Scale.steps( [ 3, 4 ] )

diminished_triad = Scale.steps( [ 3, 3 ] )

# Sevenths
minor_seventh = Scale.steps( [ 3, 4, 3 ] )

major_seventh = Scale.steps( [ 4, 3, 4 ] )

dominant_seventh = Scale.steps( [ 4, 3, 3 ] )

diminished_seventh = Scale.steps( [ 3, 3, 3 ] )

half_diminished_seventh = Scale.steps( [ 3, 3, 4 ] )

minor_major_seventh = Scale.steps( [ 3, 4, 4 ] )

# Perfect Fifth
perfect_fifth = Scale.steps( [ 7 ] )

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