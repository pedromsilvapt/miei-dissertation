from typing import Optional
from .event import MusicEvent, VoiceEvent
from ..voice import Voice

class ProgramChangeEvent ( VoiceEvent ):
    def __init__ ( self, timestamp : int, voice : Voice, program : int ):
        super().__init__( timestamp, voice )

        self.program : int = program
        
    def __str__ ( self ) -> str:
        return f"[pc=({self.program})]"

class ControlChangeEvent ( VoiceEvent ):
    def __init__ ( self, timestamp : int, voice : Voice, control : int, value : int ):
        super().__init__( timestamp, voice )

        self.control : int = control
        self.value : int = value

    def __str__ ( self ) -> str:
        return f"[cc=({self.control}, {self.value})]"

class ContextChangeEvent( VoiceEvent ):
    def __init__ ( self, timestamp : int, property : str, value, voice : Voice, staff : Optional[int] = 0 ):
        super().__init__( timestamp, voice, staff )

        self.property : str = property
        self.value = value

    def __str__ ( self ) -> str:
        return f"[{self.property}={self.value}]"
