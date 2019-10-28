from .music_node import MusicNode
from core.events import RestEvent

class RestNode( MusicNode ):
    def __init__ ( self, value = None, visible = False ):
        self.value = value
        self.visible = visible

    def get_events ( self, context ):
        rest = RestEvent(
            timestamp = context.cursor,
            duration = context.get_duration( self.value ),
            value = context.get_value( self.value ),
            channel = context.channel,
            visible = self.visible
        )

        context.cursor += rest.duration

        yield rest
