from .music_node import MusicNode
from .music_parallel_node import MusicParallelNode
from musikla.core.theory import NoteAccidental, NotePitchClasses, NotePitchClassesInv, Note, Chord, Interval
from musikla.core.events import NoteEvent, ChordEvent
from typing import List

class ChordNode( MusicNode ):
    def __init__ ( self, chord : Chord, position : (int, int) = None ):
        super().__init__( position )

        self.chord : Chord = chord
    
    def get_events ( self, context ):
        o = Interval.octaves_to_semitones( context.voice.octave )

        chord = ChordEvent(
            timestamp = context.cursor,
            pitches = [ p + o for p in self.chord.to_pitches() ],
            duration = context.get_duration( self.chord.value ),
            value = context.get_value( self.chord.value ),
            voice = context.voice,
            velocity = context.voice.velocity
        )

        context.cursor += chord.duration

        yield chord
