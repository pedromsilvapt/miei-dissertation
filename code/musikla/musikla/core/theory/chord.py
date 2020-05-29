from typing import Optional
from .note import Note
from fractions import Fraction
from typing import List, Dict
from .scales import chords

class Chord:
    # Static
    @staticmethod
    def from_abbreviature ( root_note : Note, name : str, value : Fraction = Fraction() ):
        intervals = chords[ name ]

        notes = [ root_note.clone().transpose( interval ) for interval in intervals ]
        
        return Chord( notes, name, value )

    @staticmethod
    def from_pitches ( pitches : List[int], name : str = None, value : Fraction = Fraction() ):
        notes = [ Note.from_pitch( pitch, value ) for pitch in pitches ]
        
        return Chord( notes, name, value )

    def __init__ ( self, notes : List[Note] = [], name : str = None, value : Fraction = Fraction() ):
        self.notes : List[Note] = notes
        self.name : Optional[str] = name
        self.value : Fraction = value

    def to_pitches ( self ) -> List[int]:
        return [ n.to_pitch() for n in self.notes ]
    
    def timeless ( self ):
        if self.value != None and self.value != 1:
            note = self.clone()
            note.value = None
            return note
        else:
            return self

    def clone ( self ) -> 'Chord':
        return Chord( self.notes, self.name, self.value )

    def __eq__ ( self, other ):
        if other is None:
            return False

        return int( self ) == int( other )

    def __hash__ ( self ):
        return hash( str( self ) )

    def to_string ( self, base_octave : int = 3, append_value : bool = True ) -> str:
        chord =   self.name if self.name is not None \
            else ''.join( [ n.to_string( base_octave, append_value = False ) for n in self.notes ] )

        chord = '[' + chord + ']'

        if append_value and self.value != None and self.value != 1:
            chord += str( Fraction( self.value ) )

        return chord

    def __str__ ( self ):
        return self.to_string()
