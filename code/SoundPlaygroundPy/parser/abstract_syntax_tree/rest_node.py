from .music_node import MusicNode
from core.events import RestEvent

class RestNode( MusicNode ):
    def __init__ ( self, value = None, visible = False, position : (int, int) = None ):
        super().__init__( position )
        
        self.value = value
        self.visible = visible

    def get_events ( self, context ):
        rest = RestEvent(
            timestamp = context.cursor,
            duration = context.get_duration( self.value ),
            value = context.get_value( self.value ),
            voice = context.voice,
            visible = self.visible
        )

        context.cursor += rest.duration

        yield rest
