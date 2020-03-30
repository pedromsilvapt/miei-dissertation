
from .event import MusicEvent, DurationEvent, VoiceEvent
from .note import NoteEvent, NoteOnEvent, NoteOffEvent
from ..voice import Voice
from ..theory import Note, NoteAccidental, Interval
from fractions import Fraction
from typing import Dict, List, Optional

class ChordEvent( DurationEvent ):
    def __init__ ( self, timestamp = 0, pitches : List[int] = [], name : str = None, duration = 4, voice : Voice = None, velocity = 127, value = None, tied : bool = False ):
        super().__init__( timestamp, duration, value, voice )

        self.name : str = name
        self.pitches : List[int] = pitches
        self.velocity = velocity
        self.tied : bool = tied

    @property
    def notes ( self ) -> List[NoteEvent]:
        return [ self.note_at( i ) for i in range( len( self.pitches ) ) ]

    def note_at ( self, index : int ) -> NoteEvent:
        return NoteEvent.from_pitch( 
            timestamp = self.timestamp,
            pitch = self.pitches[ index ],
            duration = self.duration,
            voice = self.voice,
            velocity = self.velocity,
            value = self.value,
            tied = self.tied
        )

    def music ( self ):
        from ..music import SharedMusic

        return SharedMusic( [ self ] )

    @property
    def chord_on ( self ) -> 'ChordOnEvent':
        return ChordOnEvent( 
            timestamp = self.timestamp, 
            pitches = self.pitches, 
            name = self.name, 
            voice = self.voice, 
            velocity = self.velocity, 
            tied = self.tied
        )

    @property
    def chord_off ( self ) -> 'ChordOffEvent':
        return ChordOffEvent( 
            timestamp = self.timestamp + self.duration, 
            pitches = self.pitches, 
            name = self.name, 
            voice = self.voice, 
            tied = self.tied
        )

    def with_root_pitch ( self, pitch : int, **kargs ) -> 'ChordEvent':
        name = kargs[ 'name' ] if 'name' in kargs else self.name

        rp : int = self.pitches[ 0 ] if self.pitches else 0

        return ChordEvent(
            timestamp = self.timestamp,
            pitches = [ pitch + ( p - rp ) for p in self.pitches ],
            name = name,
            duration = self.duration, 
            voice = self.voice, 
            velocity = self.velocity, 
            value = self.value
        )

    def with_pitches ( self, pitches : List[int], **kargs ) -> 'ChordEvent':
        name = kargs[ 'name' ] if 'name' in kargs else self.name

        return ChordEvent(
            timestamp = self.timestamp,
            pitches = pitches,
            name = name,
            duration = self.duration, 
            voice = self.voice, 
            velocity = self.velocity, 
            value = self.value
        )

    def __eq__ ( self, other ):
        if other is None or not isinstance( other, ChordEvent ):
            return False

        return len( self.pitches ) == len( other.pitches ) \
           and all( p1 == p2 for p1, p2 in zip( self.pitches, other.pitches ) )

    def __add__ ( self, interval ):
        if type( interval ) == int:
            return self.with_pitches( [ p + interval for p in self.pitches ] )
        elif isinstance( interval, Interval ):
            return self.with_pitches( [ p + int( interval ) for p in self.pitches ] )
        else:
            return self

    def __sub__ ( self, interval ):
        if type( interval ) == int:
            return self.with_pitches( [ p - interval for p in self.pitches ] )
        elif isinstance( interval, Interval ):
            return self.with_pitches( [ p - int( interval ) for p in self.pitches ] )
        else:
            return self

    def __repr__ ( self ):
        return f'[{self.timestamp}]' + str( self )

    def __str__ ( self ):
        notes = ''.join( str( n ) for n in self.notes )

        if self.name is None:
            return f"[{ notes }]"

        return f'"{ self.name }"[{ notes }]'

class ChordOnEvent( VoiceEvent ):
    def __init__ ( self, timestamp = 0, pitches : List[int] = [], name : str = None, voice : Voice = None, velocity = 127, tied : bool = False ):
        super().__init__( timestamp, voice )

        self.name : Optional[str] = name
        self.pitches : List[int] = pitches
        self.velocity = velocity
        self.tied : bool = tied

    def chord_off ( self, timestamp : int ) -> 'ChordOffEvent':
        return ChordOffEvent( 
            timestamp = timestamp, 
            pitches = self.pitches, 
            name = self.name, 
            voice = self.voice, 
            tied = self.tied
        )

    @property
    def notes ( self ) -> List[NoteEvent]:
        return [ self.note_at( i ) for i in range( len( self.pitches ) ) ]

    def note_at ( self, index : int ) -> NoteEvent:
        return NoteOnEvent.from_pitch( 
            timestamp = self.timestamp,
            pitch = self.pitches[ index ],
            voice = self.voice,
            velocity = self.velocity,
            tied = self.tied
        )

    def music ( self ):
        from ..music import SharedMusic

        return SharedMusic( [ self ] )

    def with_root_pitch ( self, pitch : int, **kargs ) -> 'ChordOnEvent':
        name = kargs[ 'name' ] if 'name' in kargs else self.name

        rp : int = self.pitches[ 0 ] if self.pitches else 0

        return ChordOnEvent(
            timestamp = self.timestamp,
            pitches = [ pitch + ( p - rp ) for p in self.pitches ],
            name = name,
            voice = self.voice, 
            velocity = self.velocity, 
        )

    def with_pitches ( self, pitches : List[int], **kargs ) -> 'ChordOnEvent':
        name = kargs[ 'name' ] if 'name' in kargs else self.name

        return ChordOnEvent(
            timestamp = self.timestamp,
            pitches = pitches,
            name = name,
            voice = self.voice, 
            velocity = self.velocity, 
        )

    def __eq__ ( self, other ):
        if other is None or not isinstance( other, ChordEvent ):
            return False

        return len( self.pitches ) == len( other.pitches ) \
           and all( p1 == p2 for p1, p2 in zip( self.pitches, other.pitches ) )

    def __add__ ( self, interval ):
        if type( interval ) == int:
            return self.with_pitches( [ p + interval for p in self.pitches ] )
        elif isinstance( interval, Interval ):
            return self.with_pitches( [ p + int( interval ) for p in self.pitches ] )
        else:
            return self

    def __sub__ ( self, interval ):
        if type( interval ) == int:
            return self.with_pitches( [ p - interval for p in self.pitches ] )
        elif isinstance( interval, Interval ):
            return self.with_pitches( [ p - int( interval ) for p in self.pitches ] )
        else:
            return self

    def __repr__ ( self ):
        return f'[{self.timestamp}]' + str( self )

    def __str__ ( self ):
        notes = ''.join( str( n.note ) for n in self.notes )

        if self.name is None:
            return f"[{ notes }](On)"

        return f'"{ self.name }"[{ notes }](On)'

class ChordOffEvent( VoiceEvent ):
    def __init__ ( self, timestamp = 0, pitches : List[int] = [], name : str = None, voice : Voice = None, tied : bool = False ):
        super().__init__( timestamp, voice )

        self.name : Optional[str] = name
        self.pitches : List[int] = pitches
        self.tied : bool = tied

    @property
    def notes ( self ) -> List[NoteOffEvent]:
        return [ self.note_at( i ) for i in range( len( self.pitches ) ) ]

    def note_at ( self, index : int ) -> NoteOffEvent:
        return NoteOffEvent.from_pitch( 
            timestamp = self.timestamp,
            pitch = self.pitches[ index ],
            voice = self.voice,
            tied = self.tied
        )

    def music ( self ):
        from ..music import SharedMusic

        return SharedMusic( [ self ] )

    def with_root_pitch ( self, pitch : int, **kargs ) -> 'ChordOffEvent':
        name = kargs[ 'name' ] if 'name' in kargs else self.name

        rp : int = self.pitches[ 0 ] if self.pitches else 0

        return ChordOffEvent(
            timestamp = self.timestamp,
            pitches = [ pitch + ( p - rp ) for p in self.pitches ],
            name = name,
            voice = self.voice,
        )

    def with_pitches ( self, pitches : List[int], **kargs ) -> 'ChordOffEvent':
        name = kargs[ 'name' ] if 'name' in kargs else self.name

        return ChordOffEvent(
            timestamp = self.timestamp,
            pitches = pitches,
            name = name,
            voice = self.voice, 
        )

    def __eq__ ( self, other ):
        if other is None or not isinstance( other, ChordEvent ):
            return False

        return len( self.pitches ) == len( other.pitches ) \
           and all( p1 == p2 for p1, p2 in zip( self.pitches, other.pitches ) )

    def __add__ ( self, interval ):
        if type( interval ) == int:
            return self.with_pitches( [ p + interval for p in self.pitches ] )
        elif isinstance( interval, Interval ):
            return self.with_pitches( [ p + int( interval ) for p in self.pitches ] )
        else:
            return self

    def __sub__ ( self, interval ):
        if type( interval ) == int:
            return self.with_pitches( [ p - interval for p in self.pitches ] )
        elif isinstance( interval, Interval ):
            return self.with_pitches( [ p - int( interval ) for p in self.pitches ] )
        else:
            return self

    def __repr__ ( self ):
        return f'[{self.timestamp}]' + str( self )

    def __str__ ( self ):
        notes = ''.join( str( n.note ) for n in self.notes )

        if self.name is None:
            return f"[{ notes }](Off)"

        return f'"{ self.name }"[{ notes }](Off)'