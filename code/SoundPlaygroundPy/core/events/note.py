
from .event import MusicEvent, DurationEvent, VoiceEvent
from ..voice import Voice
from ..theory import Note, NoteAccidental
from fractions import Fraction
from typing import Dict

class NoteOnEvent ( VoiceEvent ):
    def __init__ ( self, timestamp = 0, pitch_class = 0, octave = 4, accidental = NoteAccidental.NONE, velocity = 0, voice : Voice = None, parent : 'NoteEvent' = None ):
        self.pitch_class : int = pitch_class
        self.octave : int = octave
        self.accidental : int = accidental
        self.velocity : int = velocity
        self.parent : 'NoteEvent' = parent

        self._disabled : bool = False

        super().__init__( timestamp, voice )

    @property
    def note ( self ) -> Note:
        return Note( self.pitch_class, self.octave, self.accidental )

    def note_off ( self, timestamp : int ) -> 'NoteOffEvent':
        return NoteOffEvent( timestamp, self.pitch_class, self.octave, self.accidental, self.voice, self.parent )

    def __int__ ( self ):
        return int( self.note )

    def __str__ ( self ):
        return str( self.note ) + "(On)"


class NoteOffEvent ( VoiceEvent ):
    def __init__ ( self, timestamp = 0, pitch_class = 0, octave = 4, accidental = NoteAccidental.NONE, voice : Voice = None, parent : 'NoteEvent' = None ):
        self.pitch_class : int = pitch_class
        self.octave : int = octave
        self.accidental : int = accidental
        self.parent : 'NoteEvent' = parent

        super().__init__( timestamp, voice )

    @property
    def note ( self ) -> Note:
        return Note( self.pitch_class, self.octave, self.accidental )

    def __int__ ( self ):
        return int( self.note )

    def __str__ ( self ):
        return str( self.note ) + "(Off)"

class NoteEvent( DurationEvent ):
    def __init__ ( self, timestamp = 0, pitch_class = 0, duration = 4, octave = 4, voice : Voice = None, velocity = 127, accidental = NoteAccidental.NONE, value = None ):
        super().__init__( timestamp, duration, value, voice )

        self.pitch_class = pitch_class
        self.octave = octave
        self.velocity = velocity
        self.accidental = accidental

    @property
    def note ( self ) -> Note:
        return Note( self.pitch_class, self.octave, self.accidental, self.value )

    @property
    def note_on ( self ) -> NoteOnEvent:
        return NoteOnEvent( self.timestamp, self.pitch_class, self.octave, self.accidental, self.velocity, self.voice, parent = self )

    @property
    def note_off ( self ) -> NoteOnEvent:
        return NoteOffEvent( self.timestamp + self.duration, self.pitch_class, self.octave, self.accidental, self.voice, parent = self )

    def from_pattern ( self, pattern : 'NoteEvent' ) -> 'NoteEvent':
        return self.clone( 
             timestamp = pattern.timestamp,
             octave = self.octave + ( pattern.octave - pattern.voice.octave ),
             value = pattern.value,
             duration = pattern.duration,
             velocity = pattern.velocity,
             voice = pattern.voice
        )

    def __int__ ( self ):
        return int( self.note )

    def __str__ ( self ):
        return f'[{self.timestamp}]' + str( self.note )

