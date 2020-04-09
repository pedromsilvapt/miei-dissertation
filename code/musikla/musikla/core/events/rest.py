from ..voice import Voice
from .event import DurationEvent
from fractions import Fraction

class RestEvent( DurationEvent ):
    def __init__ ( self, timestamp = 0, duration = 0, value = 0, voice : Voice = None, visible = True ):
        super().__init__( timestamp, duration, value, voice )

        self.visible = visible

    def __repr__ ( self ):
        return f'[{self.timestamp}]' + str( self )

    def __str__ ( self ) -> str:
        rest = 'z' if self.visible else 'x'

        if self.value != None and self.value != 1:
            rest += str( Fraction( self.value ) )

        return rest
