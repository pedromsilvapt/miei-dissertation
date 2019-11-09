from fractions import Fraction
from typing import List, Dict

class NoteAccidental():
    DOUBLEFLAT = -2
    FLAT = 2
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

class Note:
    # Static
    def parse_pitch_octave ( pitch ):
        if pitch[ 0 ].islower():
            pitch_class = NotePitchClasses[ pitch[ 0 ].upper() ]
            octave = len( pitch ) - 1

            return ( pitch_class, octave )
        else:
            pitch_class = NotePitchClasses[ pitch[ 0 ] ]
            octave = -len( pitch )
            
            return ( pitch_class, octave )

    def __init__ ( self, pitch_class : int, octave : int = 0, accidental : int = 0, value : Fraction = Fraction() ):
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

        return self

    def transpose ( self, semitones : int ) -> 'Note':
        return self.with_pitch( self.to_pitch() + semitones )

        return self
    
    def clone ( self ):
        return Note( self.pitch_class, self.octave, self.accidental, self.value )

    def as_chord ( self, chord : List[int] ) -> 'Chord':
        return Chord( self, chord )

    def __int__ ( self ):
        return self.to_pitch()

    def __str__ ( self ):
        note : str = NotePitchClassesInv[ self.pitch_class ].lower()

        if self.octave <= 3:
            note = note.upper()

            for i in range( 2, self.octave - 1, -1 ): note += ","
        else:
            for i in range( 5, self.octave + 1 ): note += "'"
        
        if self.value != None and self.value != 1:
            note += str( Fraction( self.value ) )

        if self.accidental == NoteAccidental.DOUBLESHARP:
            note = '^^' + note
        elif self.accidental == NoteAccidental.SHARP:
            note = '^' + note
        elif self.accidental == NoteAccidental.FLAT:
            note = '~' + note
        elif self.accidental == NoteAccidental.DOUBLEFLAT:
            note = '~~' + note

        note += "(%s)" % int( self )

        return note

class Chord:
    def __init__ ( self, root : Note, intervals : List[int] ):
        self.root : Note = root
        self.intervals : List[int] = intervals

    def to_notes ( self ) -> List[Note]:
        notes : List[NoteNode] = []

        for semitones in self.intervals:
            notes.append( self.root.clone().transpose( semitones ) )

        return notes
