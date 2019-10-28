from .event import DurationEvent

class RestEvent( DurationEvent ):
    def __init__ ( self, timestamp = 0, duration = 0, value = 0, channel = 0, visible = True ):
        super().__init__( timestamp, duration, value, channel )

        self.visible = visible
