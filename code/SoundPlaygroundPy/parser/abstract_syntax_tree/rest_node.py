from .music_node import MusicNode

class RestNode( MusicNode ):
    def __init__ ( self, value = None, visible = False ):
        self.value = value
        self.visible = visible

    def get_events ( self, context ):
        context.cursor += context.get_duration( self.value or context.value );

        return iter(())
