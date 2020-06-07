from typing import Optional, Tuple
from ..voice import Voice
from .event import DurationEvent
from fractions import Fraction

class RestEvent( DurationEvent ):
    def __init__ ( self, timestamp = 0, duration = 0, value = 0, voice : Voice = None, visible = True, staff : Optional[int] = 0 ):
        super().__init__( timestamp, duration, value, voice, staff )

        self.visible = visible

    def to_string ( self, chars: Tuple[str, str] = ( 'z', 'x' ), append_value : bool = True ):
        rest = chars[ 0 ] if self.visible else chars[ 1 ]

        if append_value and self.value != None and self.value != 1:
            rest += str( Fraction( self.value ) )

        return rest

    def __repr__ ( self ):
        return f'[{self.timestamp}]' + str( self )

    def __str__ ( self ) -> str:
        return self.to_string()
