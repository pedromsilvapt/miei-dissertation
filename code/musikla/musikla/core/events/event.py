from typing import Callable, Any, Optional, cast
from ..voice import Voice
from copy import copy

class MusicEvent():
    def __init__ ( self, timestamp : int = 0, staff : Optional[int] = 0 ):
        self.timestamp : int = timestamp
        self.staff : Optional[int] = staff

    @property
    def end_timestamp ( self ) -> int:
        if hasattr( self, 'duration' ):
            return self.timestamp + cast( DurationEvent, self ).duration
        else:
            return self.timestamp
        
    @end_timestamp.setter 
    def end_timestamp( self, value ):
        if hasattr( self, 'duration' ):
            self.duration = value - self.timestamp
        
            if hasattr( self, 'value' ) and hasattr( self, 'value' ):
                self.value = cast( VoiceEvent, self ).voice.from_duration_absolute( self.duration )


    def clone ( self, **kargs ):
        instance = copy( self )

        for key, value in kargs.items():
            setattr( instance, key, value )
        
        return instance

    def join ( self, context ):
        if context.cursor < self.end_timestamp:
            context.cursor = self.end_timestamp

        return self

    def __add__ ( self, other ):
        return self
        
    def __sub__ ( self, other ):
        return self

    def __repr__ ( self ):
        return "<%s>(%r)" % (self.__class__.__name__, self.__dict__)

class VoiceEvent(MusicEvent):
    def __init__ ( self, timestamp : int = 0, voice : Voice = None, staff : Optional[int] = 0 ):
        super().__init__( timestamp, staff )

        self.voice : Voice = voice or Voice.unknown

class DurationEvent ( VoiceEvent ):
    def __init__ ( self, timestamp = 0, duration = 0, value = 0, voice : Voice = None, staff : Optional[int] = 0 ):
        super().__init__( timestamp, voice, staff )

        # Value stores information about the note duration independent of the tempo and time signature
        self.value = value
        # While duration stores the note's duration as milliseconds
        self.duration = duration

class CallbackEvent ( MusicEvent ):
    def __init__ ( self, timestamp : int, callback : Callable, data : Any = None ):
        super().__init__( timestamp )

        self.callback : Callable = callback
        self.data  : Any= data

    def call ( self ):
        self.callback( self.timestamp, self.data )
