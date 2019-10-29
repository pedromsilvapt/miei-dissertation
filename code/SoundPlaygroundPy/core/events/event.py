class MusicEvent():
    def __init__ ( self, timestamp = 0 ):
        self.timestamp = timestamp
        try:
            self.disabled = False
        except AttributeError: pass
    
    def __repr__ ( self ):
        return "<%s>(%r)" % (self.__class__.__name__, self.__dict__)

class DurationEvent ( MusicEvent ):
    def __init__ ( self, timestamp = 0, duration = 0, value = 0, channel = 0 ):
        super().__init__( timestamp )

        # Value stores information about the note duration independent of the tempo and time signature
        self.value = value
        # While duration stores the note's duration as milliseconds
        self.duration = duration
        self.channel = channel