from typing import Union, Optional
from fractions import Fraction
from .context import Context
from .music import Music, MusicBuffer
from .events import MusicEvent

class Metronome:
    def __init__ ( self, context : Context, beats : int = None, tick : Union[Music, MusicEvent] = None ):
        self.context : Context = context
        self.beats : Optional[int] = beats
        # self.duration : Optional[float] = float( duration ) if duration is not None else None
        self.tick : Optional[MusicEvent] = tick[ 0 ] if isinstance( tick, Music ) else tick
        
    def clone ( self ) -> 'Metronome':
        return Metronome( self.context, self.beats, self.tick )

    def _generate ( self, context : Context ):
        beats = self.beats or 0

        cursor = context.cursor

        beat_duration = self.context.voice.get_beat_duration()

        while self.beats is None or beats > 0:
            yield self.tick.clone( cursor = cursor )

            if beats > 0: beats -= 1

            cursor += beat_duration
    
    def to_music ( self, context : Context ) -> Music:
        return Music( self._generate( context ) )