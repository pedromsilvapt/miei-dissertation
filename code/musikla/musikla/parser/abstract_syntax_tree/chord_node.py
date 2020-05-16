from musikla.parser.printer import CodePrinter
from .music_node import MusicNode
from musikla.core.theory import Chord, Interval
from musikla.core.events import ChordEvent
from typing import Tuple

class ChordNode( MusicNode ):
    def __init__ ( self, chord : Chord, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.chord : Chord = chord
    
    def to_source ( self, printer : CodePrinter ):
        printer.add_token( str( self.chord ) )

    def get_events ( self, context ):
        o = Interval.octaves_to_semitones( context.voice.octave )

        chord = ChordEvent(
            timestamp = context.cursor,
            pitches = [ p + o for p in self.chord.to_pitches() ],
            duration = context.get_duration( self.chord.value ),
            value = context.get_value( self.chord.value ),
            voice = context.voice,
            velocity = context.voice.velocity,
            staff = 0
        )

        context.cursor += chord.duration

        yield chord
