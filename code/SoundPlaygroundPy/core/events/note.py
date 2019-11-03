from .event import DurationEvent
from fractions import Fraction
from typing import Dict

class NoteAccidental():
    DOUBLEFLAT = 0
    FLAT = 1
    NONE = 2
    SHARP = 3
    DOUBLESHARP = 4

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

class NoteEvent( DurationEvent ):
    def __init__ ( self, timestamp = 0, pitch_class = 0, duration = 4, octave = 4, channel = 0, velocity = 127, accidental = NoteAccidental.NONE, value = None ):
        super().__init__( timestamp, duration, value, channel )

        self.pitch_class = pitch_class
        self.octave = octave
        self.velocity = velocity
        self.accidental = accidental

    def __int__ ( self ):
        accidental = self.accidental - 2

        return ( self.octave + 1 ) * 12 + self.pitch_class + accidental

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

        return note

