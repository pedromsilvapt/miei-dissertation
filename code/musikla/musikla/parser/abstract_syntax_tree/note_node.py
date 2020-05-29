from musikla.parser.printer import CodePrinter
from .music_node import MusicNode
from .music_parallel_node import MusicParallelNode
from musikla.core.theory import NoteAccidental, NotePitchClasses, NotePitchClassesInv, Note
from musikla.core.events import NoteEvent
from typing import List, Tuple

class NoteNode( MusicNode ):
    def __init__ ( self, note : Note, position : Tuple[int, int] = None ):
        super().__init__( position )

        self.note : Note = note
    
    def to_source ( self, printer : CodePrinter ):
        printer.add_token( self.note.to_string( base_octave = 0 ) )

    def get_events ( self, context ):
        note = NoteEvent(
            timestamp = context.cursor,
            pitch_class = self.note.pitch_class,
            duration = context.get_duration( self.note.value ),
            value = context.get_value( self.note.value ),
            octave = context.voice.octave + ( self.note.octave or 0 ),
            voice = context.voice,
            velocity = context.voice.velocity,
            accidental = self.note.accidental,
            staff = 0
        )

        context.cursor += note.duration

        yield note

    def as_chord ( self, intervals : List[int] ) -> MusicParallelNode:
        notes = self.note.as_chord( intervals ).to_notes()

        nodes = [ NoteNode( note, self.position ) for note in notes ]

        return MusicParallelNode( nodes, position = self.position )
