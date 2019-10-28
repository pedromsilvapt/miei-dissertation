class MusicEvent():
    def __init__ ( self, timestamp = 0 ):
        self.timestamp = timestamp

class NoteAccidental():
    DOUBLEFLAT = 0
    FLAT = 1
    NONE = 2
    SHARP = 3
    DOUBLESHARP = 4

class Note( MusicEvent ):
    def __init__ ( self, timestamp = 0, pitch_class = 0, duration = 4, octave = 4, channel = 0, velocity = 127, accidental = NoteAccidental.NONE ):
        super().__init__( timestamp )

        self.pitch_class = pitch_class
        self.duration = duration
        self.octave = octave
        self.channel = channel
        self.velocity = velocity
        self.accidental = accidental

    def __int__ ( self ):
        accidental = self.accidental - 2

        return ( self.octave + 1 ) * 12 + self.pitch_class + accidental

    def __str__ ( self ):
        return f"<Note Timestamp={self.timestamp} PitchClass={self.pitch_class} Duration={self.duration} Octave={self.octave} Accidental={self.accidental} Channel={self.channel} Velocity={self.velocity}>"
