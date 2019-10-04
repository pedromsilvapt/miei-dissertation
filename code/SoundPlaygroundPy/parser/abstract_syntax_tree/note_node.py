from .music_node import MusicNode
from core import NoteAccidental, Note

class NoteNode( MusicNode ):
    def __init__ ( self, pitch_class = 0, value = None, octave = None, accidental = NoteAccidental.NONE ):
        super.__init__()

        self.pitch_class = pitch_class
        self.value = value
        self.octave = octave
        self.accidental = accidental
    
    def get_events ( context ):
        note = Note(
            timestamp = context.cursor,
            pitch_class = self.pitch_class,
            duration = context.get_duration( self.value or context.value ),
            octave = context.octave + ( self.octave or 0 ),
            channel = context.channel,
            velocity = context.velocity,
            accidental = self.accidental
        )

        context.cursor += note.duration

        yield note

