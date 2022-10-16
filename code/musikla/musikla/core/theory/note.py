from fractions import Fraction
from typing import List, Dict

def keysToIndexes (d : Dict) -> Dict:
    i : int = 0
    result = dict()

    for key in d.keys():
        result[ key ] = i
        i += 1

    return result

class NoteAccidental():
    DOUBLEFLAT = -2
    FLAT = -1
    NONE = 0
    SHARP = 1
    DOUBLESHARP = 2

NotePitchClasses = {
    'C': 0,
    'D': 2,
    'E': 4,
    'F': 5,
    'G': 7,
    'A': 9,
    'B': 11
}

NotePitchClassesInv : Dict[int, str] = { v: k for k, v in NotePitchClasses.items() }

NotePitchClassesIndexes : Dict[str, int] = keysToIndexes( NotePitchClasses )

class Note:
    # Static
    @staticmethod
    def parse_pitch_octave ( pitch ):
        if pitch[ 0 ].islower():
            pitch_class = NotePitchClasses[ pitch[ 0 ].upper() ]
            octave = len( pitch ) - 1

            return ( pitch_class, octave )
        else:
            pitch_class = NotePitchClasses[ pitch[ 0 ] ]
            octave = -len( pitch )

            return ( pitch_class, octave )

    @staticmethod
    def from_pitch ( pitch : int, value : Fraction = Fraction() ):
        octave = ( pitch // 12 ) - 1
        pitch_class = pitch % 12
        accidental = 0

        if pitch_class not in NotePitchClassesInv:
            pitch_class -= 1

            accidental = 1

        return Note( pitch_class, octave, accidental, value )

    def __init__ ( self, pitch_class : int = 0, octave : int = 0, accidental : int = 0, value : Fraction = Fraction() ):
        self.pitch_class : int = pitch_class
        self.octave : int = octave
        self.accidental : int = accidental
        self.value : Fraction = value

    def to_pitch ( self ) -> int:
        return ( self.octave + 1 ) * 12 + self.pitch_class + self.accidental

    def with_pitch ( self, pitch : int ) -> 'Note':
        self.octave = ( pitch // 12 ) - 1
        self.pitch_class = pitch % 12

        if self.pitch_class not in NotePitchClassesInv:
            self.pitch_class -= 1

            self.accidental = 1
        else:
            self.accidental = 0

        return self

    def transpose ( self, semitones : int ) -> 'Note':
        return self.with_pitch( self.to_pitch() + int( semitones ) )

    def timeless ( self ):
        if self.value != None and self.value != 1:
            note = self.clone()
            note.value = None
            return note
        else:
            return self

    def clone ( self ):
        return Note( self.pitch_class, self.octave, self.accidental, self.value )

    def as_chord ( self, chord : List[int] ) -> 'Chord':
        return Chord( self, chord )

    def __eq__ ( self, other ):
        if other is None:
            return False

        return int( self ) == int( other )

    def __int__ ( self ):
        return self.to_pitch()

    def __hash__ ( self ):
        return hash( str( self ) )

    def to_string ( self, base_octave : int = 4, append_value : bool = True ):
        note : str = NotePitchClassesInv[ self.pitch_class ].lower()

        if self.octave < base_octave:
            note = note.upper()

            for _ in range( base_octave - 2, self.octave - 1, -1 ): note += ","
        else:
            for _ in range( base_octave + 1, self.octave + 1 ): note += "'"

        if append_value and self.value != None and self.value != 1:
            note += str( Fraction( self.value ) )

        if self.accidental == NoteAccidental.DOUBLESHARP:
            note = '^^' + note
        elif self.accidental == NoteAccidental.SHARP:
            note = '^' + note
        elif self.accidental == NoteAccidental.FLAT:
            note = '_' + note
        elif self.accidental == NoteAccidental.DOUBLEFLAT:
            note = '__' + note

        return note

    def __str__ ( self ):
        return self.to_string()
