from .music_node import MusicNode
from core import NoteAccidental, Note

_pitch_classes_dictionary = {
    'C': 0,
    'D': 2,
    'E': 4,
    'F': 5,
    'G': 7,
    'A': 9,
    'B': 11
}

class NoteNode( MusicNode ):
    def __init__ ( self, pitch_class = 0, value = None, octave = None, accidental = NoteAccidental.NONE ):
        super().__init__()

        self.pitch_class = pitch_class
        self.value = value
        self.octave = octave
        self.accidental = accidental
    
    def get_events ( self, context ):
        note = Note(
            timestamp = context.cursor,
            pitch_class = self.pitch_class,
            duration = context.get_duration( self.value ),
            octave = context.octave + ( self.octave or 0 ),
            channel = context.channel,
            velocity = context.velocity,
            accidental = self.accidental
        )

        context.cursor += note.duration

        yield note


    # Static
    def parse_pitch_octave ( pitch ):
        if pitch[ 0 ].islower():
            pitch_class = _pitch_classes_dictionary[ pitch[ 0 ].upper() ]
            octave = len( pitch ) - 1

            return ( pitch_class, octave )
        else:
            pitch_class = _pitch_classes_dictionary[ pitch[ 0 ] ]
            octave = -len( pitch )
            
            return ( pitch_class, octave )
