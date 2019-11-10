
from .event import MusicEvent, DurationEvent
from ..theory import Note, NoteAccidental
from fractions import Fraction
from typing import Dict

class NoteOnEvent ( MusicEvent ):
    def __init__ ( self, timestamp = 0, pitch_class = 0, octave = 4, accidental = NoteAccidental.NONE, velocity = 0, channel = 0, parent : 'NoteEvent' = None ):
        super().__init__( timestamp )

        self.pitch_class : int = pitch_class
        self.octave : int = octave
        self.accidental : int = accidental
        self.velocity : int = velocity
        self.channel : int = channel
        self.parent : 'NoteEvent' = parent

        self._disabled : bool = False

    @property
    def disabled ( self ) -> bool:
        if self.parent != None:
            return self.parent.disabled
        
        return self._disabled

    @disabled.setter
    def disabled ( self, value : bool ):
        if self.parent != None:
            self.parent.disabled = value
        else:
            self._disabled = value

    @property
    def note ( self ) -> Note:
        return Note( self.pitch_class, self.octave, self.accidental )

    def __int__ ( self ):
        return int( self.note )

    def __str__ ( self ):
        return str( self.note ) + "(On)"


class NoteOffEvent ( MusicEvent ):
    def __init__ ( self, timestamp = 0, pitch_class = 0, octave = 4, accidental = NoteAccidental.NONE, channel = 0, parent : 'NoteEvent' = None ):
        super().__init__( timestamp )

        self.pitch_class : int = pitch_class
        self.octave : int = octave
        self.accidental : int = accidental
        self.channel : int = channel
        self.parent : 'NoteEvent' = parent

    @property
    def disabled ( self ) -> bool:
        if self.parent != None:
            return self.parent.disabled
        
        return self._disabled

    @disabled.setter
    def disabled ( self, value : bool ):
        if self.parent != None:
            self.parent.disabled = value
        else:
            self._disabled = value

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
        return NoteOnEvent( self.timestamp, self.pitch_class, self.octave, self.accidental, self.velocity, self.channel, parent = self )

    @property
    def note_off ( self ) -> NoteOnEvent:
        return NoteOffEvent( self.timestamp + self.duration, self.pitch_class, self.octave, self.accidental, self.channel, parent = self )

    def __int__ ( self ):
        return int( self.note )

    def __str__ ( self ):
        return str( self.note )

