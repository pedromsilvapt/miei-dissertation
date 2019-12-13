from typing import Callable, Any
from ..voice import Voice
from copy import copy

class MusicEvent():
    def __init__ ( self, timestamp : int = 0 ):
        self.timestamp : int = timestamp
        
    @property
    def end_timestamp ( self ) -> int:
        if hasattr( self, 'duration' ):
            return self.timestamp + self.duration
        else:
            return self.timestamp

    def clone ( self, **kargs ):
        instance = copy( self )

        for key, value in kargs.items():
            setattr( instance, key, value )
        
        return instance

    def join ( self, context ):
        context.cursor = self.end_timestamp

        return self

    def __repr__ ( self ):
        return "<%s>(%r)" % (self.__class__.__name__, self.__dict__)

class VoiceEvent(MusicEvent):
    def __init__ ( self, timestamp : int = 0, voice : Voice = None ):
        super().__init__( timestamp )

        self.voice : Voice = voice or Voice.unknown

class DurationEvent ( VoiceEvent ):
    def __init__ ( self, timestamp = 0, duration = 0, value = 0, voice : Voice = None ):
        super().__init__( timestamp, voice )

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
