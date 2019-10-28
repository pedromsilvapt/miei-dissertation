from .event import MusicEvent

class ProgramChangeEvent ( MusicEvent ):
    def __init__ ( self, timestamp, channel, program ):
        super().__init__( timestamp )

        self.channel = channel
        self.program = program

class ControlChangeEvent ( MusicEvent ):
    def __init__ ( self, timestamp, channel, control, value ):
        super().__init__( timestamp )

        self.channel = channel
        self.control = control
        self.value = value

class ContextChangeEvent( MusicEvent ):
    def __init__ ( self, timestamp, property, value ):
        super().__init__( timestamp )

        self.property = property
        self.value = value
