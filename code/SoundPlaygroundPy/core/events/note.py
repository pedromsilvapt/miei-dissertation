
from .event import MusicEvent, DurationEvent
from ..theory import Note, NoteAccidental
from fractions import Fraction
from typing import Dict

class NoteOnEvent ( MusicEvent ):
    def __init__ ( self, timestamp = 0, pitch_class = 0, octave = 4, accidental = NoteAccidental.NONE, velocity = 0, channel = 0 ):
        super().__init__( timestamp )

        self.pitch_class : int = pitch_class
        self.octave : int = octave
        self.accidental : int = accidental
        self.velocity : int = velocity
        self.channel = channel

    @property
    def note ( self ) -> Note:
        return Note( self.pitch_class, self.octave, self.accidental )

    def __int__ ( self ):
        return int( self.note )

    def __str__ ( self ):
        return str( self.note ) + "(On)"


class NoteOffEvent ( MusicEvent ):
    def __init__ ( self, timestamp = 0, pitch_class = 0, octave = 4, accidental = NoteAccidental.NONE, channel = 0 ):
        super().__init__( timestamp )

        self.pitch_class : int = pitch_class
        self.octave : int = octave
        self.accidental : int = accidental
        self.channel = channel

    @property
    def note ( self ) -> Note:
        return Note( self.pitch_class, self.octave, self.accidental )

    def __int__ ( self ):
        return int( self.note )

    def __str__ ( self ):
        return str( self.note ) + "(Off)"

class NoteEvent( DurationEvent ):
    def __init__ ( self, timestamp = 0, pitch_class = 0, duration = 4, octave = 4, channel = 0, velocity = 127, accidental = NoteAccidental.NONE, value = None ):
        super().__init__( timestamp, duration, value, channel )

        self.pitch_class = pitch_class
        self.octave = octave
        self.velocity = velocity
        self.accidental = accidental

    @property
    def note ( self ) -> Note:
        return Note( self.pitch_class, self.octave, self.accidental, self.value )

    @property
    def note_on ( self ) -> NoteOnEvent:
        return NoteOnEvent( self.timestamp, self.pitch_class, self.octave, self.accidental, self.velocity, self.channel )

    @property
    def note_off ( self ) -> NoteOnEvent:
        return NoteOffEvent( self.timestamp + self.duration, self.pitch_class, self.octave, self.accidental, self.channel )

    def __int__ ( self ):
        return int( self.note )

    def __str__ ( self ):
        return str( self.note )

