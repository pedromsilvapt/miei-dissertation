from .event import DurationEvent
from fractions import Fraction

class RestEvent( DurationEvent ):
    def __init__ ( self, timestamp = 0, duration = 0, value = 0, channel = 0, visible = True ):
        super().__init__( timestamp, duration, value, channel )

        self.visible = visible

    def __str__ ( self ) -> str:
        rest = 'z' if self.visible else 'x'

        if self.value != None and self.value != 1:
            rest += str( Fraction( self.value ) )

        return rest
