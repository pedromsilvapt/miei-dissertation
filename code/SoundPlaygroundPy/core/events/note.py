from .event import DurationEvent

class NoteAccidental():
    DOUBLEFLAT = 0
    FLAT = 1
    NONE = 2
    SHARP = 3
    DOUBLESHARP = 4

class NoteEvent( DurationEvent ):
    def __init__ ( self, timestamp = 0, pitch_class = 0, duration = 4, octave = 4, channel = 0, velocity = 127, accidental = NoteAccidental.NONE, value = None ):
        super().__init__( timestamp, duration, value, channel )

        self.pitch_class = pitch_class
        self.octave = octave
        self.velocity = velocity
        self.accidental = accidental

    def __int__ ( self ):
        accidental = self.accidental - 2

        return ( self.octave + 1 ) * 12 + self.pitch_class + accidental

    def __str__ ( self ):
        return f"<Note Timestamp={self.timestamp} PitchClass={self.pitch_class} Duration={self.duration} Octave={self.octave} Accidental={self.accidental} Channel={self.channel} Velocity={self.velocity}>"
