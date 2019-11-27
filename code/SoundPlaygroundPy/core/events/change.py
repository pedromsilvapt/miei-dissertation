from .event import MusicEvent, VoiceEvent
from ..voice import Voice

class ProgramChangeEvent ( VoiceEvent ):
    def __init__ ( self, timestamp : int, voice : Voice, program : int ):
        super().__init__( timestamp, voice )

        self.program : int = program

class ControlChangeEvent ( VoiceEvent ):
    def __init__ ( self, timestamp : int, voice : Voice, control : int, value : int ):
        super().__init__( timestamp, voice )

        self.control : int = control
        self.value : int = value

class ContextChangeEvent( MusicEvent ):
    def __init__ ( self, timestamp : int, property : str, value ):
        super().__init__( timestamp )

        self.property : str = property
        self.value = value

    def __str__ ( self ) -> str:
        return f"[{self.property}={self.value}]"
