from .music_node import MusicNode
from .music_parallel_node import MusicParallelNode
from core.theory import NoteAccidental, NotePitchClasses, NotePitchClassesInv, Note
from core.events import NoteEvent
from typing import List

class NoteNode( MusicNode ):
    def __init__ ( self, note : Note, position : (int, int) = None ):
        super().__init__( position )

        self.note : Note = note
    
    def get_events ( self, context ):
        note = NoteEvent(
            timestamp = context.cursor,
            pitch_class = self.note.pitch_class,
            duration = context.get_duration( self.note.value ),
            value = context.get_value( self.note.value ),
            octave = context.octave + ( self.note.octave or 0 ),
            channel = context.channel,
            velocity = context.velocity,
            accidental = self.note.accidental
        )

        context.cursor += note.duration

        yield note

    def as_chord ( self, intervals : List[int] ) -> MusicParallelNode:
        notes = self.note.as_chord( intervals ).to_notes()

        nodes = [ NoteNode( note, self.position ) for note in notes ]

        return MusicParallelNode( nodes, self.position )
