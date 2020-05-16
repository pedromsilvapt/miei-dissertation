from typing import Optional
from .event import VoiceEvent
from ..voice import Voice

BAR_STANDARD = 0
BAR_DOUBLE = 1
BAR_END = 2
BAR_BEGIN_REPEAT = 3
BAR_END_REPEAT = 4
BAR_BEGIN_END_REPEAT = 5

class BarNotationEvent ( VoiceEvent ):
    def __init__ ( self, timestamp : int, voice : Voice, staff : Optional[int] = None, kind : int = BAR_STANDARD ):
        super().__init__( timestamp, voice, staff )

        self.kind : int = kind
            
    def __str__ ( self ) -> str:
        return f"[newbar]"

class StaffNotationEvent ( VoiceEvent ):
    def __init__ ( self, timestamp : int, voice : Voice, staff : Optional[int] = None, kind : int = BAR_STANDARD ):
        super().__init__( timestamp, voice, staff )

        self.kind : int = kind

    def __str__ ( self ) -> str:
        return f"[newstaff]"

