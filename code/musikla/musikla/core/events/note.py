
from .event import DurationEvent, VoiceEvent
from ..voice import Voice
from ..theory import Note, NoteAccidental, Interval
from typing import Optional, cast

class NoteOnEvent ( VoiceEvent ):
    @staticmethod
    def from_pitch ( timestamp = 0, pitch = 0, voice : Voice = None, velocity = 127, tied : bool = False, staff : Optional[int] = 0 ):
        note = Note.from_pitch( pitch )
        
        return NoteOnEvent(
            timestamp = timestamp,
            velocity = velocity,
            voice = voice,
            pitch_class = note.pitch_class, 
            octave = note.octave, 
            accidental = note.accidental,
            tied = tied,
            staff = staff
        )

    def __init__ ( self, timestamp = 0, pitch_class = 0, octave = 4, accidental = NoteAccidental.NONE, velocity = 0, voice : Voice = None, tied : bool = False, staff : Optional[int] = 0 ):
        self.pitch_class : int = pitch_class
        self.octave : int = octave
        self.accidental : int = accidental
        self.velocity : int = velocity
        self.tied : bool = tied

        self._disabled : bool = False

        super().__init__( timestamp, voice, staff )

    @property
    def note ( self ) -> Note:
        return Note( self.pitch_class, self.octave, self.accidental )

    def note_off ( self, timestamp : int ) -> 'NoteOffEvent':
        return NoteOffEvent( timestamp, self.pitch_class, self.octave, self.accidental, self.voice, self.tied, self.staff )

    def __int__ ( self ):
        return int( self.note )

    def __str__ ( self ):
        return str( self.note ) + "(On)"


class NoteOffEvent ( VoiceEvent ):
    @staticmethod
    def from_pitch ( timestamp = 0, pitch = 0, voice : Voice = None, tied : bool = False, staff : Optional[int] = 0 ):
        note = Note.from_pitch( pitch )
        
        return NoteOffEvent(
            timestamp = timestamp,
            voice = voice,
            pitch_class = note.pitch_class, 
            octave = note.octave, 
            accidental = note.accidental,
            tied = tied,
            staff = staff
        )

    def __init__ ( self, timestamp = 0, pitch_class = 0, octave = 4, accidental = NoteAccidental.NONE, voice : Voice = None, tied : bool = False, staff : Optional[int] = 0 ):
        self.pitch_class : int = pitch_class
        self.octave : int = octave
        self.accidental : int = accidental
        self.tied : bool = tied

        super().__init__( timestamp, voice, staff )

    @property
    def note ( self ) -> Note:
        return Note( self.pitch_class, self.octave, self.accidental )

    def __int__ ( self ):
        return int( self.note )

    def __str__ ( self ):
        return str( self.note ) + "(Off)"

class NoteEvent( DurationEvent ):
    @staticmethod
    def from_pitch ( timestamp = 0, pitch = 0, duration = 4, voice : Voice = None, velocity = 127, value = None, tied : bool = False, staff : Optional[int] = 0 ):
        note = Note.from_pitch( pitch )
        
        return NoteEvent(
            timestamp = timestamp,
            duration = duration,
            value = value,
            velocity = velocity,
            voice = voice,
            pitch_class = note.pitch_class, 
            octave = note.octave, 
            accidental = note.accidental,
            tied = tied,
            staff = staff
        )

    def __init__ ( self, timestamp = 0, pitch_class = 0, duration = 4, octave = 4, voice : Voice = None, velocity = 127, accidental = NoteAccidental.NONE, value = None, tied : bool = False, staff : Optional[int] = 0 ):
        super().__init__( timestamp, duration, value, voice, staff )

        self.pitch_class = pitch_class
        self.octave = octave
        self.velocity = velocity
        self.accidental = accidental
        self.tied = tied

    def music ( self ):
        from ..music import SharedMusic

        return SharedMusic( [ self ] )

    @property
    def note ( self ) -> Note:
        return Note( self.pitch_class, self.octave, self.accidental, self.value )

    @property
    def note_on ( self ) -> NoteOnEvent:
        return NoteOnEvent( self.timestamp, self.pitch_class, self.octave, self.accidental, self.velocity, self.voice, self.tied, self.staff )

    @property
    def note_off ( self ) -> NoteOffEvent:
        return NoteOffEvent( self.timestamp + self.duration, self.pitch_class, self.octave, self.accidental, self.voice, self.tied, self.staff )

    def from_pattern ( self, pattern : 'NoteEvent' ) -> 'NoteEvent':
        return cast( NoteEvent, self.clone( 
             timestamp = pattern.timestamp,
             octave = self.octave + ( pattern.octave - pattern.voice.octave ),
             value = pattern.value,
             duration = pattern.duration,
             velocity = pattern.velocity,
             voice = pattern.voice,
             staff = pattern.staff
        ) )

    def with_pitch ( self, pitch : int ) -> 'NoteEvent':
        return NoteEvent.from_pitch(
            timestamp = self.timestamp,
            pitch = pitch,
            duration = self.duration, 
            voice = self.voice, 
            velocity = self.velocity, 
            value = self.value,
            tied = self.tied,
            staff = self.staff
        )

    def __lt__ ( self, other ):
        if other is None: return False

        return int( self ) < int( other )

    def __le__ ( self, other ):
        if other is None: return False

        return int( self ) <= int( other )

    def __eq__ ( self, other ):
        if other is None or not isinstance( other, NoteEvent ):
            return False

        return int( self ) == int( other )

    def __add__ ( self, interval ):
        if type( interval ) == int:
            return self.with_pitch( int( self ) + interval )
        elif isinstance( interval, Interval ):
            return self.with_pitch( int( self ) + int( interval ) )
        else:
            return self

    def __sub__ ( self, interval ):
        if type( interval ) == int:
            return self.with_pitch( int( self ) - interval )
        elif isinstance( interval, Interval ):
            return self.with_pitch( int( self ) - int( interval ) )
        else:
            return self

    def __int__ ( self ):
        return int( self.note )

    def __repr__ ( self ):
        return f'[{self.timestamp}]' + str( self.note )

    def __str__ ( self ):
        return str( self.note )

