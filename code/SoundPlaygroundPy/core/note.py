class MusicEvent():
    def __init__ ( self, timestamp = 0 ):
        self.timestamp = timestamp

class NoteAccidental():
    FLAT = 0
    NONE = 1
    SHARP = 2

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
        accidental = self.accidental - 1

        return self.octave * 12 + self.pitch_class + accidental

    def __str__ ( self ):
        return f"<Note Timestamp={self.timestamp} PitchClass={self.pitch_class} Duration={self.duration} Octave={self.octave} Accidental={self.accidental} Channel={self.channel} Velocity={self.velocity}>"
